import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import brandService from '../../services/brandService';
import './BrandAIManagement.css';

const BrandAIManagement = () => {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('overview');
    const [loading, setLoading] = useState(false);
    const [aiStatus, setAiStatus] = useState(null);
    const [brandInsights, setBrandInsights] = useState(null);
    const [trainingHistory, setTrainingHistory] = useState([]);
    const [knowledgeBase, setKnowledgeBase] = useState([]);
    const [responseTemplates, setResponseTemplates] = useState([]);
    const [conversationPatterns, setConversationPatterns] = useState([]);
    const [newKnowledge, setNewKnowledge] = useState({
        type: 'faq',
        question: '',
        answer: '',
        keywords: [],
        language: 'en'
    });
    const [newTemplate, setNewTemplate] = useState({
        template_name: '',
        template_text: '',
        category: '',
        urgency: '',
        language: 'en',
        variables: []
    });

    useEffect(() => {
        loadAIData();
    }, []);

    const loadAIData = async () => {
        setLoading(true);
        try {
            const [status, insights, history, knowledge, templates, patterns] = await Promise.all([
                brandService.getAIStatus(),
                brandService.getBrandAIInsights(),
                brandService.getTrainingHistory(),
                brandService.getBrandKnowledge(),
                brandService.getResponseTemplates(),
                brandService.getConversationPatterns()
            ]);

            setAiStatus(status);
            setBrandInsights(insights);
            setTrainingHistory(history);
            setKnowledgeBase(knowledge);
            setResponseTemplates(templates);
            setConversationPatterns(patterns);
        } catch (error) {
            console.error('Error loading AI data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleTrainModels = async () => {
        try {
            setLoading(true);
            const result = await brandService.trainModels();
            alert(result.message);
            loadAIData(); // Reload data
        } catch (error) {
            console.error('Error training models:', error);
            alert('Error training models');
        } finally {
            setLoading(false);
        }
    };

    const handleAddKnowledge = async () => {
        try {
            setLoading(true);
            const result = await brandService.addBrandKnowledge(newKnowledge);
            alert(result.message);
            setNewKnowledge({
                type: 'faq',
                question: '',
                answer: '',
                keywords: [],
                language: 'en'
            });
            loadAIData();
        } catch (error) {
            console.error('Error adding knowledge:', error);
            alert('Error adding knowledge');
        } finally {
            setLoading(false);
        }
    };

    const handleAddTemplate = async () => {
        try {
            setLoading(true);
            const result = await brandService.addResponseTemplate(newTemplate);
            alert(result.message);
            setNewTemplate({
                template_name: '',
                template_text: '',
                category: '',
                urgency: '',
                language: 'en',
                variables: []
            });
            loadAIData();
        } catch (error) {
            console.error('Error adding template:', error);
            alert('Error adding template');
        } finally {
            setLoading(false);
        }
    };

    const renderOverview = () => (
        <div className="ai-overview">
            <div className="ai-status-grid">
                <div className="status-card">
                    <h3>AI Engine Status</h3>
                    <div className="status-indicators">
                        <div className={`status-indicator ${aiStatus?.ai_engine_status?.openai_available ? 'success' : 'error'}`}>
                            OpenAI: {aiStatus?.ai_engine_status?.openai_available ? 'Available' : 'Unavailable'}
                        </div>
                        <div className={`status-indicator ${aiStatus?.ai_engine_status?.google_nlp_available ? 'success' : 'error'}`}>
                            Google NLP: {aiStatus?.ai_engine_status?.google_nlp_available ? 'Available' : 'Unavailable'}
                        </div>
                        <div className={`status-indicator ${aiStatus?.ai_engine_status?.ml_models_loaded ? 'success' : 'warning'}`}>
                            ML Models: {aiStatus?.ai_engine_status?.ml_models_loaded ? 'Loaded' : 'Not Loaded'}
                        </div>
                    </div>
                </div>

                <div className="status-card">
                    <h3>Training Status</h3>
                    <div className="training-info">
                        <p>Total Learning Data: {aiStatus?.training_status?.total_learning_data || 0}</p>
                        <p>Recent Learning Data: {aiStatus?.training_status?.recent_learning_data || 0}</p>
                        <p>Intent Model Accuracy: {aiStatus?.training_status?.latest_intent_model?.accuracy?.toFixed(3) || 'N/A'}</p>
                        <p>Urgency Model Accuracy: {aiStatus?.training_status?.latest_urgency_model?.accuracy?.toFixed(3) || 'N/A'}</p>
                    </div>
                </div>

                <div className="status-card">
                    <h3>Conversation Stats</h3>
                    <div className="conversation-info">
                        <p>Active Conversations: {aiStatus?.conversation_stats?.active_conversations || 0}</p>
                        <p>Completed Conversations: {aiStatus?.conversation_stats?.completed_conversations || 0}</p>
                        <p>Avg Turns per Conversation: {aiStatus?.conversation_stats?.avg_turns_per_conversation?.toFixed(2) || 'N/A'}</p>
                    </div>
                </div>
            </div>

            <div className="action-buttons">
                <button 
                    className="btn btn-primary" 
                    onClick={handleTrainModels}
                    disabled={loading}
                >
                    {loading ? 'Training...' : 'Train Models'}
                </button>
                <button 
                    className="btn btn-secondary" 
                    onClick={loadAIData}
                    disabled={loading}
                >
                    Refresh Data
                </button>
            </div>
        </div>
    );

    const renderInsights = () => (
        <div className="ai-insights">
            <div className="insights-grid">
                <div className="insight-card">
                    <h3>Learning Insights</h3>
                    <div className="insight-data">
                        <p>Knowledge Base Size: {brandInsights?.knowledge_base?.total_entries || 0}</p>
                        <p>Recent Interactions: {brandInsights?.recent_learning_data || 0}</p>
                        <p>Top Patterns: {brandInsights?.conversation_patterns?.length || 0}</p>
                    </div>
                </div>

                <div className="insight-card">
                    <h3>Language Distribution</h3>
                    <div className="language-chart">
                        {brandInsights?.learning_insights?.language_distribution && 
                            Object.entries(brandInsights.learning_insights.language_distribution).map(([lang, count]) => (
                                <div key={lang} className="language-bar">
                                    <span>{lang.toUpperCase()}</span>
                                    <div className="bar" style={{width: `${(count / Math.max(...Object.values(brandInsights.learning_insights.language_distribution))) * 100}%`}}></div>
                                    <span>{count}</span>
                                </div>
                            ))
                        }
                    </div>
                </div>
            </div>

            <div className="patterns-section">
                <h3>Top Conversation Patterns</h3>
                <div className="patterns-list">
                    {brandInsights?.conversation_patterns?.slice(0, 10).map((pattern, index) => (
                        <div key={index} className="pattern-item">
                            <div className="pattern-header">
                                <span className="pattern-type">{pattern.type}</span>
                                <span className="pattern-frequency">Used {pattern.frequency} times</span>
                            </div>
                            <p className="pattern-text">{pattern.text}</p>
                            <div className="pattern-meta">
                                <span>Category: {pattern.category}</span>
                                <span>Urgency: {pattern.urgency}</span>
                                <span>Success Rate: {(pattern.success_rate * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );

    const renderKnowledge = () => (
        <div className="knowledge-management">
            <div className="knowledge-form">
                <h3>Add New Knowledge</h3>
                <div className="form-group">
                    <label>Type:</label>
                    <select 
                        value={newKnowledge.type} 
                        onChange={(e) => setNewKnowledge({...newKnowledge, type: e.target.value})}
                    >
                        <option value="faq">FAQ</option>
                        <option value="common_issues">Common Issues</option>
                        <option value="product_info">Product Info</option>
                    </select>
                </div>
                <div className="form-group">
                    <label>Question:</label>
                    <input 
                        type="text" 
                        value={newKnowledge.question}
                        onChange={(e) => setNewKnowledge({...newKnowledge, question: e.target.value})}
                        placeholder="Enter question or issue"
                    />
                </div>
                <div className="form-group">
                    <label>Answer:</label>
                    <textarea 
                        value={newKnowledge.answer}
                        onChange={(e) => setNewKnowledge({...newKnowledge, answer: e.target.value})}
                        placeholder="Enter answer or solution"
                        rows="3"
                    />
                </div>
                <div className="form-group">
                    <label>Keywords (comma-separated):</label>
                    <input 
                        type="text" 
                        value={newKnowledge.keywords.join(', ')}
                        onChange={(e) => setNewKnowledge({...newKnowledge, keywords: e.target.value.split(',').map(k => k.trim())})}
                        placeholder="keyword1, keyword2, keyword3"
                    />
                </div>
                <div className="form-group">
                    <label>Language:</label>
                    <select 
                        value={newKnowledge.language} 
                        onChange={(e) => setNewKnowledge({...newKnowledge, language: e.target.value})}
                    >
                        <option value="en">English</option>
                        <option value="hi">Hindi</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                    </select>
                </div>
                <button 
                    className="btn btn-primary" 
                    onClick={handleAddKnowledge}
                    disabled={loading || !newKnowledge.question || !newKnowledge.answer}
                >
                    Add Knowledge
                </button>
            </div>

            <div className="knowledge-list">
                <h3>Knowledge Base</h3>
                <div className="knowledge-items">
                    {knowledgeBase.map((item, index) => (
                        <div key={index} className="knowledge-item">
                            <div className="knowledge-header">
                                <span className="knowledge-type">{item.type}</span>
                                <span className="knowledge-language">{item.language}</span>
                            </div>
                            <h4>{item.question}</h4>
                            <p>{item.answer}</p>
                            <div className="knowledge-meta">
                                <span>Usage: {item.usage_count}</span>
                                <span>Success Rate: {(item.success_rate * 100).toFixed(1)}%</span>
                                <span>Keywords: {item.keywords?.join(', ')}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );

    const renderTemplates = () => (
        <div className="template-management">
            <div className="template-form">
                <h3>Add Response Template</h3>
                <div className="form-group">
                    <label>Template Name:</label>
                    <input 
                        type="text" 
                        value={newTemplate.template_name}
                        onChange={(e) => setNewTemplate({...newTemplate, template_name: e.target.value})}
                        placeholder="Enter template name"
                    />
                </div>
                <div className="form-group">
                    <label>Template Text:</label>
                    <textarea 
                        value={newTemplate.template_text}
                        onChange={(e) => setNewTemplate({...newTemplate, template_text: e.target.value})}
                        placeholder="Enter template text with {variables}"
                        rows="4"
                    />
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <label>Category:</label>
                        <select 
                            value={newTemplate.category} 
                            onChange={(e) => setNewTemplate({...newTemplate, category: e.target.value})}
                        >
                            <option value="">Any</option>
                            <option value="complaint">Complaint</option>
                            <option value="feedback">Feedback</option>
                            <option value="suggestion">Suggestion</option>
                            <option value="support">Support</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Urgency:</label>
                        <select 
                            value={newTemplate.urgency} 
                            onChange={(e) => setNewTemplate({...newTemplate, urgency: e.target.value})}
                        >
                            <option value="">Any</option>
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Language:</label>
                        <select 
                            value={newTemplate.language} 
                            onChange={(e) => setNewTemplate({...newTemplate, language: e.target.value})}
                        >
                            <option value="en">English</option>
                            <option value="hi">Hindi</option>
                            <option value="es">Spanish</option>
                            <option value="fr">French</option>
                        </select>
                    </div>
                </div>
                <button 
                    className="btn btn-primary" 
                    onClick={handleAddTemplate}
                    disabled={loading || !newTemplate.template_name || !newTemplate.template_text}
                >
                    Add Template
                </button>
            </div>

            <div className="template-list">
                <h3>Response Templates</h3>
                <div className="template-items">
                    {responseTemplates.map((template, index) => (
                        <div key={index} className="template-item">
                            <div className="template-header">
                                <h4>{template.name}</h4>
                                <span className="template-language">{template.language}</span>
                            </div>
                            <p>{template.text}</p>
                            <div className="template-meta">
                                <span>Category: {template.category || 'Any'}</span>
                                <span>Urgency: {template.urgency || 'Any'}</span>
                                <span>Usage: {template.usage_count}</span>
                                <span>Success Rate: {(template.success_rate * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );

    const renderTraining = () => (
        <div className="training-management">
            <div className="training-overview">
                <h3>Model Training History</h3>
                <div className="training-stats">
                    <div className="stat-card">
                        <h4>Intent Classifier</h4>
                        <p>Latest Accuracy: {trainingHistory.find(h => h.model_type === 'intent_classifier')?.accuracy_score?.toFixed(3) || 'N/A'}</p>
                        <p>Training Samples: {trainingHistory.find(h => h.model_type === 'intent_classifier')?.training_samples || 'N/A'}</p>
                    </div>
                    <div className="stat-card">
                        <h4>Urgency Classifier</h4>
                        <p>Latest Accuracy: {trainingHistory.find(h => h.model_type === 'urgency_classifier')?.accuracy_score?.toFixed(3) || 'N/A'}</p>
                        <p>Training Samples: {trainingHistory.find(h => h.model_type === 'urgency_classifier')?.training_samples || 'N/A'}</p>
                    </div>
                </div>
            </div>

            <div className="training-history">
                <h3>Recent Training Sessions</h3>
                <div className="history-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Model Type</th>
                                <th>Version</th>
                                <th>Samples</th>
                                <th>Accuracy</th>
                                <th>Duration</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {trainingHistory.slice(0, 10).map((record, index) => (
                                <tr key={index}>
                                    <td>{record.model_type}</td>
                                    <td>{record.model_version}</td>
                                    <td>{record.training_samples}</td>
                                    <td>{(record.accuracy_score * 100).toFixed(1)}%</td>
                                    <td>{record.training_duration ? `${record.training_duration.toFixed(1)}s` : 'N/A'}</td>
                                    <td>{new Date(record.created_at).toLocaleDateString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );

    if (loading && !aiStatus) {
        return <div className="loading">Loading AI Management...</div>;
    }

    return (
        <div className="brand-ai-management">
            <div className="ai-header">
                <h2>AI Management & Self-Learning</h2>
                <p>Monitor and manage your AI system's learning capabilities and performance</p>
            </div>

            <div className="ai-tabs">
                <button 
                    className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                    onClick={() => setActiveTab('overview')}
                >
                    Overview
                </button>
                <button 
                    className={`tab ${activeTab === 'insights' ? 'active' : ''}`}
                    onClick={() => setActiveTab('insights')}
                >
                    Insights
                </button>
                <button 
                    className={`tab ${activeTab === 'knowledge' ? 'active' : ''}`}
                    onClick={() => setActiveTab('knowledge')}
                >
                    Knowledge Base
                </button>
                <button 
                    className={`tab ${activeTab === 'templates' ? 'active' : ''}`}
                    onClick={() => setActiveTab('templates')}
                >
                    Response Templates
                </button>
                <button 
                    className={`tab ${activeTab === 'training' ? 'active' : ''}`}
                    onClick={() => setActiveTab('training')}
                >
                    Training History
                </button>
            </div>

            <div className="ai-content">
                {activeTab === 'overview' && renderOverview()}
                {activeTab === 'insights' && renderInsights()}
                {activeTab === 'knowledge' && renderKnowledge()}
                {activeTab === 'templates' && renderTemplates()}
                {activeTab === 'training' && renderTraining()}
            </div>
        </div>
    );
};

export default BrandAIManagement; 