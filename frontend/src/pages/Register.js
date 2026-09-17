import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { formatApiError } from '../services/api';
import Button from '../components/ui/Button';
import { Input, Select } from '../components/ui/Input';
import { Mail, Lock, User, Phone } from 'lucide-react';
import './Auth.css';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone: '',
    role: 'HR',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { register } = useAuth();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const payload = {
        ...formData,
        role: formData.role === 'CANDIDATE' ? 'CANDIDATE' : 'HR',
      };
      await register(payload);
      navigate('/login');
    } catch (err) {
      setError(formatApiError(err, 'Registration failed. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box" style={{ maxWidth: '480px' }}>
        <div className="auth-header">
          <div className="auth-logo-badge">⚡</div>
          <h1>Create an Account</h1>
          <p className="auth-subtitle">Join the intelligent AI recruitment ecosystem</p>
        </div>

        {error && (
          <div className="alert alert-error" style={{ marginBottom: '16px' }}>
            <span>⚠️ {error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <Select
            label="I am joining as a"
            name="role"
            value={formData.role}
            onChange={handleChange}
          >
            <option value="HR">Company Owner / Founder / HR</option>
            <option value="CANDIDATE">Candidate (Looking for opportunities)</option>
          </Select>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <Input
              label="First Name"
              name="first_name"
              icon={User}
              value={formData.first_name}
              onChange={handleChange}
              placeholder="e.g. John"
              required
            />
            <Input
              label="Last Name"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              placeholder="e.g. Doe"
              required
            />
          </div>

          <Input
            label="Work Email"
            name="email"
            type="email"
            icon={Mail}
            value={formData.email}
            onChange={handleChange}
            placeholder="name@company.com"
            required
          />

          <Input
            label="Password"
            name="password"
            type="password"
            icon={Lock}
            value={formData.password}
            onChange={handleChange}
            placeholder="Min. 8 characters"
            required
          />

          <Input
            label="Phone (Optional)"
            name="phone"
            icon={Phone}
            value={formData.phone}
            onChange={handleChange}
            placeholder="+1 (555) 000-0000"
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            loading={loading}
            style={{ width: '100%', marginTop: '8px' }}
          >
            Create Account & Get Started
          </Button>
        </form>

        <div className="auth-footer">
          Already registered? <Link to="/login">Sign in here</Link>
        </div>
      </div>
    </div>
  );
}
