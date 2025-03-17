import axios from 'axios';

const API_URL = 'http://localhost:5000/api'; // Update with your backend URL

export const loginUser = async (credentials) => {
    try {
        const response = await axios.post(`${API_URL}/login`, credentials);
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

export const registerUser = async (userData) => {
    try {
        const response = await axios.post(`${API_URL}/register`, userData);
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

export const uploadDocument = async (formData) => {
    try {
        const response = await axios.post(`${API_URL}/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};

export const checkEligibility = async (userId) => {
    try {
        const response = await axios.get(`${API_URL}/eligibility/${userId}`);
        return response.data;
    } catch (error) {
        throw error.response.data;
    }
};