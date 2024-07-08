import React, { useState } from 'react';
import axios from 'axios';
import '../css/ImageUpload.css';

const ImageUpload = ({ onUpload, width = '420px', height = '200px' }) => {
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    await uploadFile(file);
  };

  const handleDrop = async (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    await uploadFile(file);
  };

  const uploadFile = async (file) => {
    setError(null);
    setSuccess(null);
    try {
      const formData = new FormData();
      formData.append('file', file);

      //for live server
      // const response = await axios.post('https://forteam22ict.xyz/main/upload-image', formData, {
      //   headers: {
      //     'Content-Type': 'multipart/form-data',
      //   },
      // });
      //for localhost
      const response = await axios.post('http://localhost:5000/main/upload-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      if (response.status === 200 && response.data.file_path) {
        const uploadedUrl = response.data.file_path;
        onUpload(uploadedUrl);
        setSuccess('Image uploaded successfully.');
      } else if (response.data.error) {
        setError(`Error: ${response.data.error}`);
      } else {
        setError('Failed to upload image');
      }
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(`Error: ${err.response.data.error}`);
      } else {
        setError(err.message);
      }
    }
  };

  return (
    <div className="image-upload-wrapper">
      <div
        className="image-upload-container"
        style={{ width: width, height: height }} // Set the width and height dynamically
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
      >
        <input type="file" onChange={handleFileChange} />
        <p>Drag & drop an image here, or click to select one</p>
      </div>
      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}
    </div>
  );
};

export default ImageUpload;
