import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

// Companies API
export const companiesAPI = {
  create: (data) => api.post('/companies', data),
  list: () => api.get('/companies'),
  get: (id) => api.get(`/companies/${id}`),
  update: (id, data) => api.put(`/companies/${id}`, data),
  delete: (id) => api.delete(`/companies/${id}`),
  addMember: (companyId, data) => api.post(`/companies/${companyId}/members`, data),
  getMembers: (companyId) => api.get(`/companies/${companyId}/members`),
  removeMember: (companyId, userId) => api.delete(`/companies/${companyId}/members/${userId}`),
};

// Jobs API
export const jobsAPI = {
  create: (companyId, data) => api.post(`/companies/${companyId}/jobs`, data),
  list: (companyId, params) => api.get(`/companies/${companyId}/jobs`, { params }),
  listPublished: (params) => api.get('/jobs', { params }),
  getPublished: (jobId) => api.get(`/jobs/${jobId}`),
  get: (companyId, jobId) => api.get(`/companies/${companyId}/jobs/${jobId}`),
  update: (companyId, jobId, data) => api.put(`/companies/${companyId}/jobs/${jobId}`, data),
  delete: (companyId, jobId) => api.delete(`/companies/${companyId}/jobs/${jobId}`),
  publish: (companyId, jobId) => api.patch(`/companies/${companyId}/jobs/${jobId}/publish`),
  close: (companyId, jobId) => api.patch(`/companies/${companyId}/jobs/${jobId}/close`),
  archive: (companyId, jobId) => api.patch(`/companies/${companyId}/jobs/${jobId}/archive`),
};

// Candidates API
export const candidatesAPI = {
  createProfile: (data) => api.post('/candidates/profile', data),
  getProfile: () => api.get('/candidates/profile'),
  updateProfile: (data) => api.put('/candidates/profile', data),
};

// Resumes API
export const resumesAPI = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/candidates/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: () => api.get('/candidates/resumes'),
  download: (resumeId) => api.get(`/candidates/resumes/${resumeId}/download`),
};

// Matching API
export const matchingAPI = {
  matchCandidate: (jobId, candidateId, companyId) =>
    api.post(
      `/matching/jobs/${jobId}/candidates/${candidateId}?company_id=${companyId}`
    ),
};

// Applications API
export const applicationsAPI = {
  apply: (jobId) => api.post(`/applications/jobs/${jobId}`),
  getApplicants: (jobId, companyId) =>
    api.get(`/applications/jobs/${jobId}`, {
      params: { company_id: companyId },
    }),
  getDetails: (applicationId, companyId) =>
    api.get(`/applications/${applicationId}`, {
      params: { company_id: companyId },
    }),
  shortlist: (applicationId, companyId) =>
    api.patch(
      `/applications/${applicationId}/shortlist`,
      null,
      { params: { company_id: companyId } }
    ),
  reject: (applicationId, companyId) =>
    api.patch(
      `/applications/${applicationId}/reject`,
      null,
      { params: { company_id: companyId } }
    ),
  getMyApplications: () => api.get('/applications/my'),
  getMyApplication: (applicationId) => api.get(`/applications/my/${applicationId}`),
};

// Interviews API
export const interviewsAPI = {
  schedule: (data, companyId) =>
    api.post('/interviews', data, {
      params: companyId ? { company_id: companyId } : {},
    }),
  getMyInterviews: () => api.get('/interviews/my'),
  listCompanyInterviews: (companyId) =>
    api.get('/interviews', {
      params: companyId ? { company_id: companyId } : {},
    }),
  get: (interviewId, companyId) =>
    api.get(`/interviews/${interviewId}`, {
      params: companyId ? { company_id: companyId } : {},
    }),
  confirm: (interviewId) =>
    api.patch(`/interviews/${interviewId}/confirm`),
  cancel: (interviewId, companyId) =>
    api.patch(`/interviews/${interviewId}/cancel`, null, {
      params: companyId ? { company_id: companyId } : {},
    }),
  complete: (interviewId, companyId) =>
    api.patch(`/interviews/${interviewId}/complete`, null, {
      params: companyId ? { company_id: companyId } : {},
    }),
  noShow: (interviewId, companyId) =>
    api.patch(`/interviews/${interviewId}/no-show`, null, {
      params: companyId ? { company_id: companyId } : {},
    }),
  feedback: (interviewId, data, companyId) =>
    api.post(`/interviews/${interviewId}/feedback`, data, {
      params: companyId ? { company_id: companyId } : {},
    }),
};

// Notifications API
export const notificationsAPI = {
  list: (params) => api.get('/notifications', { params }),
  markAsRead: (notificationId) =>
    api.patch(`/notifications/${notificationId}/read`),
};

// HR Applications API
export const hrApplicationsAPI = {
  getAllApplications: (companyId, status) =>
    api.get('/hr/applications', {
      params: {
        ...(companyId ? { company_id: companyId } : {}),
        ...(status && status !== 'ALL' ? { status } : {}),
      },
    }),
  getJobApplications: (jobId, companyId, status) =>
    api.get(`/hr/applications/jobs/${jobId}`, {
      params: {
        company_id: companyId,
        ...(status && status !== 'ALL' ? { status } : {}),
      },
    }),
  getApplicationDetail: (applicationId, companyId) =>
    api.get(`/hr/applications/${applicationId}`, {
      params: { company_id: companyId },
    }),
};

// AI Screening API
export const screeningAPI = {
  screenApplication: (applicationId, companyId) =>
    api.post(`/screening/applications/${applicationId}`, null, {
      params: { company_id: companyId },
    }),
  getScreeningResult: (applicationId, companyId) =>
    api.get(`/screening/applications/${applicationId}`, {
      params: { company_id: companyId },
    }),
};

// Offers API (HR / Company)
export const offersAPI = {
  list: (companyId) =>
    api.get('/offers', {
      params: companyId ? { company_id: companyId } : {},
    }),
  get: (offerId, companyId) =>
    api.get(`/offers/${offerId}`, {
      params: companyId ? { company_id: companyId } : {},
    }),
  create: (companyId, data) =>
    api.post('/offers', data, {
      params: companyId ? { company_id: companyId } : {},
    }),
  updateStatus: (offerId, statusData, companyId) =>
    api.patch(
      `/offers/${offerId}/status`,
      typeof statusData === 'string' ? { status: statusData } : statusData,
      {
        params: companyId ? { company_id: companyId } : {},
      }
    ),
};

// Candidate Offers API
export const candidateOffersAPI = {
  list: () => api.get('/candidate/offers'),
  get: (offerId) => api.get(`/candidate/offers/${offerId}`),
  accept: (offerId) => api.patch(`/candidate/offers/${offerId}/accept`),
  decline: (offerId) => api.patch(`/candidate/offers/${offerId}/decline`),
};

// Hiring Decision API (HR)
export const hiringAPI = {
  makeDecision: (applicationId, decisionData, companyId) =>
    api.patch(
      `/hiring/applications/${applicationId}/decision`,
      typeof decisionData === 'string'
        ? { decision: decisionData }
        : decisionData,
      {
        params: companyId ? { company_id: companyId } : {},
      }
    ),
};

// System Health API (Admin / Real Backend Monitoring)
export const systemAPI = {
  health: () => api.get('/health'),
  database: () => api.get('/health/database'),
};

// Error Formatter: Converts FastAPI / Pydantic 422 error objects ({type, loc, msg, input}) into human-readable strings
export const formatApiError = (err, fallback = 'An unexpected error occurred.') => {
  if (!err) return fallback;
  const detail = err.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        if (typeof d === 'string') return d;
        if (d && typeof d === 'object') {
          const field = Array.isArray(d.loc)
            ? d.loc.filter((l) => l !== 'body').join('.')
            : '';
          const message = d.msg || JSON.stringify(d);
          return field ? `${field}: ${message}` : message;
        }
        return String(d);
      })
      .join(' | ');
  }
  if (detail && typeof detail === 'object') {
    return detail.msg || JSON.stringify(detail);
  }
  return err.message || fallback;
};

export default api;


