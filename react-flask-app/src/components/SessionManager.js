import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';

const SessionManager = ({ setSsid }) => {
    const saveSessionToLocalStorage = (ssid) => {
        localStorage.setItem('ssid', ssid);
    };

    const getSessionFromLocalStorage = () => {
        return localStorage.getItem('ssid');
    };

    useEffect(() => {
        const checkSession = async (ssid) => {
            try {
                const response = await fetch(`/main/sessions/${ssid}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    // Session exists, use the existing session
                    setSsid(ssid);
                    console.log("Session exists and is valid:", ssid);
                } else if (response.status === 404) {
                    // Session does not exist, create a new one
                    console.log("Session not found on server, creating new session");
                    createSession();
                } else {
                    throw new Error('Failed to check session');
                }
            } catch (error) {
                console.error('Error checking session:', error);
                createSession(); // Fallback to creating a new session on error
            }
        };

        const createSession = async () => {
            try {
                const response = await fetch('/main/sessions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    throw new Error('Failed to create session');
                }

                const data = await response.json();
                saveSessionToLocalStorage(data.ssid);
                setSsid(data.ssid);
                console.log('New session created:', data);
            } catch (error) {
                console.error('Error creating session:', error);
            }
        };

        const storedSsid = getSessionFromLocalStorage();
        if (storedSsid) {
            // Validate the stored session ID with the server
            checkSession(storedSsid);
        } else {
            // No session ID in local storage; create a new session
            createSession();
        }
    }, [setSsid]);

    return null;
};

SessionManager.propTypes = {
    setSsid: PropTypes.func.isRequired,
};

export default SessionManager;