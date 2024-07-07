import React, { useState } from 'react';
import axios from 'axios';

const ImageUpload = ({ onUpload }) => {
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

      const response = await axios.post('http://localhost:5000/main/upload-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Server response:', response.data); // Debugging

      if (response.status === 200 && response.data.url) {
        const uploadedUrl = response.data.url;
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
    <div
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      style={{ border: '2px dashed #ccc', padding: '20px', textAlign: 'center' }}
    >
      <input type="file" onChange={handleFileChange} />
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {success && <p style={{ color: 'green' }}>{success}</p>}
    </div>
  );
};

export default ImageUpload;