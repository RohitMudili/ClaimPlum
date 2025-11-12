import { useState, useEffect } from 'react';
import { uploadClaim, processClaim } from '../services/api';
import { validateFileType, validateFileSize, formatFileSize } from '../utils/helpers';
import fileIcon from '../assets/file-icon.webp';
import fileUploadIcon from '../assets/file-upload-icon.webp';

const ClaimUpload = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    member_id: '',
    prescription: null,
    bill: null,
    member_name: '',
    contact_email: '',
    contact_phone: '',
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [displayProgress, setDisplayProgress] = useState(0);
  const [dragActive, setDragActive] = useState({ prescription: false, bill: false });

  useEffect(() => {
    if (loading && uploadProgress == 0) {
      setDisplayProgress(0);
    }else if (loading && uploadProgress > 0){
      const timer = setTimeout(() => { setDisplayProgress(uploadProgress); }, 500);
      return () => clearTimeout(timer);
    }else if (!loading){
      setDisplayProgress(0);
    }

  }, [loading, uploadProgress]);

  useEffect(() => {
    window.scrollTo(0,0);
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error for this field
    setErrors(prev => ({ ...prev, [name]: null }));
  };

  const handleFileChange = (e, type) => {
    const file = e.target.files?.[0];
    if (file) {
      validateAndSetFile(file, type);
    }
  };

  const validateAndSetFile = (file, type) => {
    // Validate file type
    if (!validateFileType(file)) {
      setErrors(prev => ({ ...prev, [type]: 'Only PDF, PNG, JPG, JPEG files are allowed' }));
      return;
    }

    // Validate file size (10MB)
    if (!validateFileSize(file, 10 * 1024 * 1024)) {
      setErrors(prev => ({ ...prev, [type]: 'File size must be less than 10MB' }));
      return;
    }

    setFormData(prev => ({ ...prev, [type]: file }));
    setErrors(prev => ({ ...prev, [type]: null }));
  };

  const handleDrag = (e, type) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(prev => ({ ...prev, [type]: true }));
    } else if (e.type === 'dragleave') {
      setDragActive(prev => ({ ...prev, [type]: false }));
    }
  };

  const handleDrop = (e, type) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(prev => ({ ...prev, [type]: false }));

    const file = e.dataTransfer.files?.[0];
    if (file) {
      validateAndSetFile(file, type);
    }
  };

  const validate = () => {
    const newErrors = {};

    // Member ID is required
    if (!formData.member_id || !formData.member_id.trim()) {
      newErrors.member_id = 'Member ID is required';
    }

    //Prescription file required
    if (!formData.prescription) {
      newErrors.prescription = 'Prescription file is required';
    }

    // Bill file required
    if (!formData.bill) {
      newErrors.bill = 'Bill file is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setLoading(true);
    setUploadProgress(0);

    try {
      // Step 1: Upload documents
      setUploadProgress(30);
      const uploadResult = await uploadClaim(formData);

      // Check if it's a non-member (sales conversion)
      if (uploadResult.decision === 'NOT_A_MEMBER') {
        setUploadProgress(100);
        if (onSuccess) {
          onSuccess(uploadResult, 'NOT_A_MEMBER');
        }
        return;
      }

      // Check if claim was rejected (e.g., missing documents)
      if (uploadResult.decision === 'REJECTED') {
        setUploadProgress(100);
        if (onSuccess) {
          onSuccess(uploadResult, 'REJECTED');
        }
        return;
      }

      // Step 2: Process claim
      setUploadProgress(60);
      const processResult = await processClaim(uploadResult.claim_id);

      setUploadProgress(100);

      // Success - call callback
      if (onSuccess) {
        onSuccess({ ...processResult, claim_id: uploadResult.claim_id }, 'MEMBER');
      }

      // Reset form
      setFormData({
        member_id: '',
        prescription: null,
        bill: null,
        member_name: '',
        contact_email: '',
        contact_phone: '',
      });
      setUploadProgress(0);

    } catch (error) {
      console.error('Claim submission error:', error);
      setErrors({ submit: error.response?.data?.detail || 'Failed to submit claim. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const FileUploadZone = ({ type, label, file, error }) => (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {typeof label === 'string' ? label : label}
      </label>
      <div
        className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-all ${
          dragActive[type]
            ? 'border-primary-500 bg-primary-50'
            : error
            ? 'border-red-300 bg-red-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={(e) => handleDrag(e, type)}
        onDragLeave={(e) => handleDrag(e, type)}
        onDragOver={(e) => handleDrag(e, type)}
        onDrop={(e) => handleDrop(e, type)}
      >
        <input
          type="file"
          id={type}
          className="hidden"
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={(e) => handleFileChange(e, type)}
          disabled={loading}
        />
        <label htmlFor={type} className="cursor-pointer">
          {file ? (
            <div className="space-y-2">
              <img src={fileIcon} alt="File Icon" className="h-10 w-10 mx-auto" />
              <div className="text-sm font-medium text-gray-700">{file.name}</div>
              <div className="text-xs text-gray-500">{formatFileSize(file.size)}</div>
              <button
                type="button"
                className="text-sm text-primary-600 hover:text-primary-700"
                onClick={(e) => {
                  e.preventDefault();
                  setFormData(prev => ({ ...prev, [type]: null }));
                }}
              >
                Change file
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <img src={fileUploadIcon} alt="Upload Icon" className="h-10 w-10 mx-auto" />
              <div className="text-sm text-gray-600">
                <span className="font-medium text-primary-600">Click to upload</span> or drag and drop
              </div>
              <div className="text-xs text-gray-500">PDF, PNG, JPG, JPEG (max 10MB)</div>
            </div>
          )}
        </label>
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="mb-8">
          <h2 className="text-4xl font-bold text-gray-900 tracking-tight mb-2">Submit New Claim</h2>
          <p className="text-gray-600 font-medium">Please upload your prescription and bill to process your OPD claim</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Member ID */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Member ID <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="member_id"
              value={formData.member_id}
              onChange={handleInputChange}
              className={`w-full px-4 py-2 border rounded-lg focus:border-transparent ${
                errors.member_id ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="e.g., EMP001"
              disabled={loading}
            />
            {errors.member_id && <p className="mt-1 text-sm text-red-600">{errors.member_id}</p>}
          </div>

          {/* File Uploads */}
          <div className="grid md:grid-cols-2 gap-6">
            <FileUploadZone
              type="prescription"
              label={<>Prescription <span className="text-red-500">*</span></>}
              file={formData.prescription}
              error={errors.prescription}
            /> 
            <FileUploadZone
              type="bill"
              label={<>Bill <span className="text-red-500">*</span></>}
              file={formData.bill}
              error={errors.bill}
            />
          </div>

          {/* Optional: Contact Info for Non-Members */}
          <details className="border border-gray-200 rounded-lg p-4">
            <summary className="cursor-pointer text-sm font-medium text-gray-700">
              Optional: Contact Information (for new members)
            </summary>
            <div className="mt-4 space-y-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Full Name</label>
                <input
                  type="text"
                  name="member_name"
                  value={formData.member_name}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  placeholder="John Doe"
                  disabled={loading}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Email</label>
                <input
                  type="email"
                  name="contact_email"
                  value={formData.contact_email}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  placeholder="john@company.com"
                  disabled={loading}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Phone</label>
                <input
                  type="tel"
                  name="contact_phone"
                  value={formData.contact_phone}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  placeholder="+91-XXXXX-XXXXX"
                  disabled={loading}
                />
              </div>
            </div>
          </details>



          {/* Error Message */}
          {errors.submit && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">{errors.submit}</p>
            </div>
          )}

          {/* Progress Indicator / Submit Button */}
          {loading ? (
            <div className="space-y-3 py-2">
              <div className="flex justify-between items-center text-sm">
                <span className="font-medium text-gray-700">
                  {uploadProgress < 35 ? 'Uploading documents...' :
                   uploadProgress < 65 ? 'Validating claim details...' :
                   uploadProgress < 95 ? 'Processing claim...' :
                   'Finalizing...'}
                </span>
                <span className="text-gray-600 tabular-nums font-medium">{displayProgress}%</span>
              </div>
              <div className="relative w-full bg-gray-100 rounded-full h-3 overflow-hidden shadow-inner">
                <div
                  className="absolute top-0 left-0 h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full transition-all duration-500 ease-out shadow-sm"
                  style={{ width: `${displayProgress}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 text-center">Please don't close this window</p>
            </div>
          ) : (
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-primary-600 to-primary-700 text-white py-3.5 px-6 rounded-full font-semibold hover:from-primary-700 hover:to-primary-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-200 shadow-sm hover:shadow-md active:scale-[0.99]"
            >
              Submit Claim
            </button>
          )}
        </form>
      </div>
    </div>
  );
};

export default ClaimUpload;