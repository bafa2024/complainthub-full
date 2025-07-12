# backend/app/services/seo_indexing_service.py

import logging
import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Ticket, Brand, User
from app.core.ai_engine import AIEngine
import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path

logger = logging.getLogger(__name__)

class SEOIndexingService:
    """
    Voice Transcription SEO Indexing Service
    
    Features:
    - Generate static HTML pages for public complaints
    - Create SEO-optimized content from voice transcriptions
    - Generate sitemaps and robots.txt
    - Extract keywords and entities for SEO
    - Create structured data (JSON-LD)
    - Generate meta descriptions and titles
    - Support for multiple languages
    """
    
    def __init__(self, db: Session, output_dir: str = "static_pages"):
        self.db = db
        self.ai_engine = AIEngine()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # SEO configuration
        self.seo_config = {
            "base_url": "https://complainthub.example.com",
            "default_language": "en",
            "supported_languages": ["en", "hi", "es", "fr", "de"],
            "max_pages_per_sitemap": 50000,
            "static_page_retention_days": 365
        }
    
    def generate_seo_content_from_transcription(self, ticket_id: int) -> Dict[str, Any]:
        """
        Generate SEO-optimized content from voice transcription
        """
        try:
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if not ticket or not ticket.transcript:
                return {"success": False, "error": "Ticket or transcript not found"}
            
            # Analyze transcription with AI
            analysis = self.ai_engine.classify_intent_and_extract_details(
                ticket.transcript,
                brand_context=f"Brand: {ticket.brand.name if ticket.brand else 'Unknown'}"
            )
            
            # Extract SEO elements
            seo_elements = self._extract_seo_elements(ticket, analysis)
            
            # Generate structured data
            structured_data = self._generate_structured_data(ticket, analysis)
            
            # Create meta tags
            meta_tags = self._generate_meta_tags(ticket, seo_elements)
            
            # Generate content summary
            content_summary = self._generate_content_summary(ticket, analysis)
            
            return {
                "success": True,
                "seo_elements": seo_elements,
                "structured_data": structured_data,
                "meta_tags": meta_tags,
                "content_summary": content_summary,
                "language": analysis.get("language", "en")
            }
            
        except Exception as e:
            logger.error(f"Error generating SEO content: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_seo_elements(self, ticket: Ticket, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract SEO elements from ticket and AI analysis
        """
        # Extract keywords from transcript
        keywords = self._extract_keywords(ticket.transcript)
        
        # Extract entities
        entities = analysis.get("entities", [])
        entity_names = [entity.get("name", "") for entity in entities if entity.get("name")]
        
        # Generate title
        title = self._generate_seo_title(ticket, analysis)
        
        # Generate description
        description = self._generate_seo_description(ticket, analysis)
        
        # Determine category and tags
        category = ticket.category.value.lower()
        tags = [category, ticket.urgency.value, analysis.get("category", "complaint")]
        
        # Add brand-specific tags
        if ticket.brand:
            tags.extend([ticket.brand.name.lower(), ticket.brand.industry.lower() if ticket.brand.industry else ""])
        
        return {
            "title": title,
            "description": description,
            "keywords": keywords,
            "entities": entity_names,
            "category": category,
            "tags": [tag for tag in tags if tag],
            "sentiment": analysis.get("sentiment", "neutral"),
            "urgency": ticket.urgency.value,
            "severity": ticket.severity_level
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text using AI and NLP
        """
        try:
            # Use AI engine to extract keywords
            keywords = self.ai_engine.extract_keywords(text)
            
            # Add common complaint-related keywords
            complaint_keywords = [
                "customer service", "complaint", "issue", "problem", "resolution",
                "feedback", "support", "help", "assistance", "service quality"
            ]
            
            # Combine and deduplicate
            all_keywords = list(set(keywords + complaint_keywords))
            
            # Limit to top 10 keywords
            return all_keywords[:10]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return ["complaint", "customer service", "feedback"]
    
    def _generate_seo_title(self, ticket: Ticket, analysis: Dict[str, Any]) -> str:
        """
        Generate SEO-optimized title
        """
        brand_name = ticket.brand.name if ticket.brand else "Company"
        category = analysis.get("category", "complaint").title()
        
        # Create title based on content
        if ticket.title:
            title = f"{ticket.title} - {brand_name} Customer Service"
        else:
            title = f"{category} about {brand_name} - Customer Service Issue"
        
        # Limit title length for SEO
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title
    
    def _generate_seo_description(self, ticket: Ticket, analysis: Dict[str, Any]) -> str:
        """
        Generate SEO-optimized description
        """
        brand_name = ticket.brand.name if ticket.brand else "Company"
        
        # Use transcript or description
        content = ticket.transcript or ticket.description or ""
        
        # Clean and truncate content
        description = re.sub(r'\s+', ' ', content).strip()
        description = description[:150] + "..." if len(description) > 150 else description
        
        # Add context
        description = f"Customer {analysis.get('category', 'complaint')} about {brand_name}. {description}"
        
        return description
    
    def _generate_structured_data(self, ticket: Ticket, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate JSON-LD structured data
        """
        brand_name = ticket.brand.name if ticket.brand else "Unknown Company"
        brand_url = f"https://{ticket.brand.domain}" if ticket.brand and hasattr(ticket.brand, 'domain') else ""
        
        structured_data = {
            "@context": "https://schema.org",
            "@type": "Complaint",
            "name": ticket.title or f"Customer {analysis.get('category', 'complaint')}",
            "description": ticket.transcript or ticket.description,
            "dateCreated": ticket.created_at.isoformat(),
            "dateModified": ticket.updated_at.isoformat() if ticket.updated_at else ticket.created_at.isoformat(),
            "author": {
                "@type": "Person",
                "name": ticket.owner.full_name if ticket.owner else "Anonymous Customer"
            },
            "about": {
                "@type": "Organization",
                "name": brand_name,
                "url": brand_url
            },
            "category": analysis.get("category", "complaint"),
            "severity": ticket.severity_level,
            "urgency": ticket.urgency.value,
            "status": ticket.status.value
        }
        
        # Add satisfaction rating if available
        if ticket.satisfaction_rating:
            structured_data["reviewRating"] = {
                "@type": "Rating",
                "ratingValue": ticket.satisfaction_rating,
                "bestRating": 5
            }
        
        return structured_data
    
    def _generate_meta_tags(self, ticket: Ticket, seo_elements: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate meta tags for HTML
        """
        return {
            "title": seo_elements["title"],
            "description": seo_elements["description"],
            "keywords": ", ".join(seo_elements["keywords"]),
            "author": "ComplaintHub",
            "robots": "index, follow",
            "og:title": seo_elements["title"],
            "og:description": seo_elements["description"],
            "og:type": "article",
            "og:url": f"{self.seo_config['base_url']}/complaint/{ticket.id}",
            "twitter:card": "summary",
            "twitter:title": seo_elements["title"],
            "twitter:description": seo_elements["description"]
        }
    
    def _generate_content_summary(self, ticket: Ticket, analysis: Dict[str, Any]) -> str:
        """
        Generate human-readable content summary
        """
        brand_name = ticket.brand.name if ticket.brand else "Company"
        category = analysis.get("category", "complaint").title()
        
        summary = f"""
        <div class="complaint-summary">
            <h2>Customer {category} Summary</h2>
            <p><strong>Brand:</strong> {brand_name}</p>
            <p><strong>Issue Type:</strong> {category}</p>
            <p><strong>Urgency:</strong> {ticket.urgency.value.title()}</p>
            <p><strong>Status:</strong> {ticket.status.value.title()}</p>
            <p><strong>Reported:</strong> {ticket.created_at.strftime('%B %d, %Y')}</p>
            
            <h3>Issue Description</h3>
            <p>{ticket.transcript or ticket.description}</p>
            
            <h3>Resolution Status</h3>
            <p>This complaint is currently {ticket.status.value.replace('_', ' ')}.</p>
        </div>
        """
        
        return summary.strip()
    
    def generate_static_page(self, ticket_id: int) -> Dict[str, Any]:
        """
        Generate static HTML page for a ticket
        """
        try:
            # Get SEO content
            seo_content = self.generate_seo_content_from_transcription(ticket_id)
            if not seo_content["success"]:
                return seo_content
            
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            
            # Generate HTML content
            html_content = self._generate_html_page(ticket, seo_content)
            
            # Save to file
            filename = f"complaint_{ticket_id}.html"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Static page generated: {filepath}")
            
            return {
                "success": True,
                "filepath": str(filepath),
                "filename": filename,
                "url": f"{self.seo_config['base_url']}/static/{filename}",
                "seo_content": seo_content
            }
            
        except Exception as e:
            logger.error(f"Error generating static page: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_html_page(self, ticket: Ticket, seo_content: Dict[str, Any]) -> str:
        """
        Generate complete HTML page
        """
        meta_tags = seo_content["meta_tags"]
        structured_data = seo_content["structured_data"]
        content_summary = seo_content["content_summary"]
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Meta Tags -->
    <title>{meta_tags['title']}</title>
    <meta name="description" content="{meta_tags['description']}">
    <meta name="keywords" content="{meta_tags['keywords']}">
    <meta name="author" content="{meta_tags['author']}">
    <meta name="robots" content="{meta_tags['robots']}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{meta_tags['og:title']}">
    <meta property="og:description" content="{meta_tags['og:description']}">
    <meta property="og:type" content="{meta_tags['og:type']}">
    <meta property="og:url" content="{meta_tags['og:url']}">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="{meta_tags['twitter:card']}">
    <meta name="twitter:title" content="{meta_tags['twitter:title']}">
    <meta name="twitter:description" content="{meta_tags['twitter:description']}">
    
    <!-- Structured Data -->
    <script type="application/ld+json">
    {json.dumps(structured_data, indent=2)}
    </script>
    
    <!-- Styles -->
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .complaint-summary {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .complaint-summary h2 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        .complaint-summary h3 {{
            color: #495057;
            border-bottom: 2px solid #007bff;
            padding-bottom: 5px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.875rem;
            font-weight: 500;
        }}
        .status-new {{ background-color: #17a2b8; color: white; }}
        .status-in-progress {{ background-color: #ffc107; color: #212529; }}
        .status-resolved {{ background-color: #28a745; color: white; }}
        .status-closed {{ background-color: #6c757d; color: white; }}
    </style>
</head>
<body>
    <header>
        <h1>{meta_tags['title']}</h1>
        <p class="meta">
            Published on {ticket.created_at.strftime('%B %d, %Y')} | 
            Status: <span class="status-badge status-{ticket.status.value}">{ticket.status.value.title()}</span>
        </p>
    </header>
    
    <main>
        {content_summary}
        
        <div class="additional-info">
            <h3>Additional Information</h3>
            <p>This complaint was submitted through our voice complaint system and has been transcribed for public transparency.</p>
            <p>For more information about this complaint or to submit your own, visit our <a href="{self.seo_config['base_url']}">main complaint portal</a>.</p>
        </div>
    </main>
    
    <footer>
        <p>&copy; 2024 ComplaintHub. All rights reserved.</p>
    </footer>
</body>
</html>
        """
        
        return html_template.strip()
    
    def generate_sitemap(self, include_private: bool = False) -> Dict[str, Any]:
        """
        Generate XML sitemap for all public complaints
        """
        try:
            # Get public tickets
            query = self.db.query(Ticket).filter(
                Ticket.is_public == True,
                Ticket.deleted_at.is_(None)
            )
            
            if not include_private:
                query = query.filter(Ticket.status.in_(["resolved", "closed"]))
            
            tickets = query.order_by(Ticket.created_at.desc()).all()
            
            # Create sitemap XML
            root = ET.Element("urlset")
            root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
            
            # Add main pages
            main_pages = [
                ("/", 1.0, "daily"),
                ("/complaints", 0.9, "daily"),
                ("/brands", 0.8, "weekly"),
                ("/contact", 0.7, "monthly")
            ]
            
            for url, priority, changefreq in main_pages:
                url_elem = ET.SubElement(root, "url")
                ET.SubElement(url_elem, "loc").text = f"{self.seo_config['base_url']}{url}"
                ET.SubElement(url_elem, "priority").text = str(priority)
                ET.SubElement(url_elem, "changefreq").text = changefreq
                ET.SubElement(url_elem, "lastmod").text = datetime.utcnow().strftime("%Y-%m-%d")
            
            # Add complaint pages
            for ticket in tickets:
                url_elem = ET.SubElement(root, "url")
                ET.SubElement(url_elem, "loc").text = f"{self.seo_config['base_url']}/complaint/{ticket.id}"
                ET.SubElement(url_elem, "priority").text = "0.6"
                ET.SubElement(url_elem, "changefreq").text = "weekly"
                ET.SubElement(url_elem, "lastmod").text = ticket.updated_at.strftime("%Y-%m-%d") if ticket.updated_at else ticket.created_at.strftime("%Y-%m-%d")
            
            # Save sitemap
            sitemap_path = self.output_dir / "sitemap.xml"
            tree = ET.ElementTree(root)
            tree.write(sitemap_path, encoding="utf-8", xml_declaration=True)
            
            logger.info(f"Sitemap generated with {len(tickets)} complaint URLs")
            
            return {
                "success": True,
                "sitemap_path": str(sitemap_path),
                "total_urls": len(tickets) + len(main_pages),
                "complaint_urls": len(tickets)
            }
            
        except Exception as e:
            logger.error(f"Error generating sitemap: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_robots_txt(self) -> Dict[str, Any]:
        """
        Generate robots.txt file
        """
        try:
            robots_content = f"""
User-agent: *
Allow: /

# Sitemap
Sitemap: {self.seo_config['base_url']}/static/sitemap.xml

# Disallow private areas
Disallow: /admin/
Disallow: /api/
Disallow: /brand/
Disallow: /user/
Disallow: /auth/

# Allow public complaints
Allow: /complaint/
Allow: /complaints
Allow: /brands
Allow: /contact
"""
            
            robots_path = self.output_dir / "robots.txt"
            with open(robots_path, 'w', encoding='utf-8') as f:
                f.write(robots_content.strip())
            
            logger.info(f"robots.txt generated: {robots_path}")
            
            return {
                "success": True,
                "robots_path": str(robots_path)
            }
            
        except Exception as e:
            logger.error(f"Error generating robots.txt: {e}")
            return {"success": False, "error": str(e)}
    
    def bulk_generate_static_pages(self, limit: int = 100) -> Dict[str, Any]:
        """
        Bulk generate static pages for multiple tickets
        """
        try:
            # Get public tickets that need static pages
            tickets = self.db.query(Ticket).filter(
                Ticket.is_public == True,
                Ticket.transcript.isnot(None),
                Ticket.deleted_at.is_(None)
            ).order_by(Ticket.created_at.desc()).limit(limit).all()
            
            generated_pages = []
            failed_pages = []
            
            for ticket in tickets:
                result = self.generate_static_page(ticket.id)
                if result["success"]:
                    generated_pages.append(result)
                else:
                    failed_pages.append({"ticket_id": ticket.id, "error": result["error"]})
            
            # Generate sitemap and robots.txt
            sitemap_result = self.generate_sitemap()
            robots_result = self.generate_robots_txt()
            
            return {
                "success": True,
                "generated_pages": len(generated_pages),
                "failed_pages": len(failed_pages),
                "total_processed": len(tickets),
                "sitemap_generated": sitemap_result["success"],
                "robots_generated": robots_result["success"],
                "failed_details": failed_pages
            }
            
        except Exception as e:
            logger.error(f"Error in bulk generation: {e}")
            return {"success": False, "error": str(e)}
    
    def cleanup_old_pages(self, days: int = 365) -> Dict[str, Any]:
        """
        Clean up old static pages
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Find old tickets
            old_tickets = self.db.query(Ticket).filter(
                Ticket.updated_at < cutoff_date,
                Ticket.is_public == True
            ).all()
            
            deleted_files = []
            failed_deletions = []
            
            for ticket in old_tickets:
                filename = f"complaint_{ticket.id}.html"
                filepath = self.output_dir / filename
                
                if filepath.exists():
                    try:
                        filepath.unlink()
                        deleted_files.append(filename)
                    except Exception as e:
                        failed_deletions.append({"filename": filename, "error": str(e)})
            
            return {
                "success": True,
                "deleted_files": len(deleted_files),
                "failed_deletions": len(failed_deletions),
                "deleted_filenames": deleted_files,
                "failed_details": failed_deletions
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old pages: {e}")
            return {"success": False, "error": str(e)}
    
    def get_seo_analytics(self, brand_id: Optional[int] = None, days: int = 30) -> Dict[str, Any]:
        """
        Get SEO analytics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = self.db.query(Ticket).filter(
                Ticket.is_public == True,
                Ticket.created_at >= cutoff_date,
                Ticket.transcript.isnot(None)
            )
            
            if brand_id:
                query = query.filter(Ticket.brand_id == brand_id)
            
            tickets = query.all()
            
            # Calculate analytics
            total_tickets = len(tickets)
            tickets_with_transcripts = len([t for t in tickets if t.transcript])
            
            # Language distribution
            languages = {}
            for ticket in tickets:
                if ticket.transcript:
                    analysis = self.ai_engine.classify_intent_and_extract_details(ticket.transcript)
                    lang = analysis.get("language", "en")
                    languages[lang] = languages.get(lang, 0) + 1
            
            # Category distribution
            categories = {}
            for ticket in tickets:
                cat = ticket.category.value
                categories[cat] = categories.get(cat, 0) + 1
            
            return {
                "success": True,
                "analytics": {
                    "total_public_tickets": total_tickets,
                    "tickets_with_transcripts": tickets_with_transcripts,
                    "transcript_coverage": round((tickets_with_transcripts / total_tickets * 100) if total_tickets > 0 else 0, 2),
                    "language_distribution": languages,
                    "category_distribution": categories,
                    "static_pages_generated": len(list(self.output_dir.glob("complaint_*.html")))
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting SEO analytics: {e}")
            return {"success": False, "error": str(e)} 