// This is a mocked service for the chat functionality.

const sendMessage = async (message) => {
    console.log("Sending message to mock backend:", message);
    
    // Simulate a bot response after a short delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    const botResponses = [
        "I see. Could you please provide the order number related to your issue?",
        "Thank you. Can you confirm the date this occurred?",
        "I understand. I am creating a ticket for you now. An agent will review it shortly."
    ];
    
    // Return a random response for demonstration purposes
    const randomResponse = botResponses[Math.floor(Math.random() * botResponses.length)];

    return {
        sender: 'bot',
        text: randomResponse,
        timestamp: new Date().toISOString()
    };
};

export default {
    sendMessage
};