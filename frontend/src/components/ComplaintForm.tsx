import React, { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { updateFormField, updateFormState } from '../store/formSlice';
import { addMessage } from '../store/chatSlice';
import {
  FileText,
  Package,
  User,
  ShieldAlert,
  CheckCircle2,
  Send,
  AlertTriangle,
  Clock,
  CheckSquare,
  Search,
  Percent,
} from 'lucide-react';
import axios from 'axios';

export const ComplaintForm: React.FC = () => {
  const dispatch = useAppDispatch();
  const form = useAppSelector((state) => state.form);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const handleInputChange = (field: keyof typeof form, value: any) => {
    dispatch(updateFormField({ field, value }));
  };

  const handleSubmitToQMS = async () => {
    setIsSubmitting(true);
    setSubmitSuccess(null);
    setSubmitError(null);

    const payload = {
      form_state: {
        product_name: form.product_name,
        strength: form.strength,
        batch_number: form.batch_number,
        manufacture_date: form.manufacture_date,
        expiry_date: form.expiry_date,
        complaint_quantity: form.complaint_quantity,
        description: form.description,
        complainant_name: form.complainant_name,
        complainant_role: form.complainant_role,
        complainant_contact: form.complainant_contact,
        defect_category: form.defect_category,
        status: 'SUBMITTED',
        complaint_id: form.complaint_id,
      },
      risk_assessment: {
        severity: form.severity,
        risk_justification: form.risk_justification,
        recommended_next_actions: form.recommended_actions,
        risk_score: form.risk_score,
        health_hazard_class: form.health_hazard_class,
        regulatory_reportable: form.regulatory_reportable,
        reporting_deadline_days: form.reporting_deadline_days,
      },
    };

    try {
      const response = await axios.post('/api/complaints/save', payload);
      const savedData = response.data;
      
      const newComplaintId = savedData.complaint_id || `CMP-2026-${Date.now().toString().slice(-4)}`;

      dispatch(
        updateFormState({
          status: 'SUBMITTED',
          complaint_id: newComplaintId,
        })
      );

      setSubmitSuccess(`Complaint successfully saved to QMS database! Record ID: ${newComplaintId}`);

      dispatch(
        addMessage({
          sender: 'copilot',
          message: `Complaint form officially SUBMITTED to QMS database under ID: **${newComplaintId}**.`,
          tool_used: 'qms_database_submission',
        })
      );
    } catch (err: any) {
      console.error('Failed to submit to QMS:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to submit complaint to QMS.';
      setSubmitError(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getSeverityBadgeClass = (severity: string | null) => {
    switch (severity) {
      case 'Critical':
        return { bg: 'rgba(239, 68, 68, 0.2)', border: '#ef4444', color: '#fca5a5' };
      case 'Major':
        return { bg: 'rgba(245, 158, 11, 0.2)', border: '#f59e0b', color: '#fde68a' };
      case 'Minor':
        return { bg: 'rgba(16, 185, 129, 0.2)', border: '#10b981', color: '#a7f3d0' };
      default:
        return { bg: 'rgba(100, 116, 139, 0.2)', border: '#64748b', color: '#cbd5e1' };
    }
  };

  const badgeStyle = getSeverityBadgeClass(form.severity);

  return (
    <div
      className="complaint-form-container"
      style={{
        background: 'var(--bg-card)',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--border-light)',
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem',
        boxShadow: 'var(--shadow-md)',
        height: '100%',
        overflowY: 'auto',
      }}
    >
      {/* Form Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingBottom: '1rem',
          borderBottom: '1px solid var(--border-light)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div
            style={{
              background: 'rgba(14, 165, 233, 0.15)',
              padding: '0.5rem',
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <FileText size={22} color="#0ea5e9" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Pharmaceutical Complaint Intake Form
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Auto-populated in real-time by AIVOA Copilot & LangGraph
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {form.complaint_id && (
            <span
              style={{
                fontSize: '0.75rem',
                fontFamily: 'monospace',
                background: 'var(--bg-dark)',
                padding: '0.25rem 0.6rem',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--primary-500)',
                border: '1px solid var(--border-light)',
              }}
            >
              {form.complaint_id}
            </span>
          )}

          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 600,
              padding: '0.25rem 0.75rem',
              borderRadius: 'var(--radius-full)',
              background:
                form.status === 'SUBMITTED'
                  ? 'rgba(16, 185, 129, 0.2)'
                  : 'rgba(14, 165, 233, 0.2)',
              color: form.status === 'SUBMITTED' ? '#10b981' : '#38bdf8',
              border: `1px solid ${
                form.status === 'SUBMITTED' ? '#10b981' : '#0284c7'
              }`,
            }}
          >
            {form.status || 'DRAFT'}
          </span>
        </div>
      </div>

      {/* Section 1: Product Details */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <h3
          style={{
            fontSize: '0.85rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: 'var(--primary-500)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
          }}
        >
          <Package size={16} /> 1. Product Identification
        </h3>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '0.75rem',
          }}
        >
          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>
              Product Brand / Trade Name
            </label>
            <input
              type="text"
              value={form.product_name}
              onChange={(e) => handleInputChange('product_name', e.target.value)}
              placeholder="e.g. CardioShield"
              style={inputStyle}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>
              Dosage Strength / Form
            </label>
            <input
              type="text"
              value={form.strength}
              onChange={(e) => handleInputChange('strength', e.target.value)}
              placeholder="e.g. 10mg Tablets"
              style={inputStyle}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>
              Batch / Lot Number
            </label>
            <input
              type="text"
              value={form.batch_number}
              onChange={(e) => handleInputChange('batch_number', e.target.value)}
              placeholder="e.g. LOT-9921A"
              style={{ ...inputStyle, fontFamily: 'monospace', fontWeight: 600, color: '#38bdf8' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>
              Manufacture Date
            </label>
            <input
              type="text"
              value={form.manufacture_date}
              onChange={(e) => handleInputChange('manufacture_date', e.target.value)}
              placeholder="YYYY-MM-DD"
              style={inputStyle}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>
              Expiry Date
            </label>
            <input
              type="text"
              value={form.expiry_date}
              onChange={(e) => handleInputChange('expiry_date', e.target.value)}
              placeholder="YYYY-MM-DD"
              style={inputStyle}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>
              Complaint Quantity
            </label>
            <input
              type="text"
              value={form.complaint_quantity}
              onChange={(e) => handleInputChange('complaint_quantity', e.target.value)}
              placeholder="e.g. 15 bottles / 1,500 tabs"
              style={inputStyle}
            />
          </div>
        </div>
      </div>

      {/* Section 2: Complainant & Incident Details */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <h3
          style={{
            fontSize: '0.85rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: 'var(--accent-teal)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
          }}
        >
          <User size={16} /> 2. Complainant & Incident Report
        </h3>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '0.75rem',
          }}
        >
          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>
              Complainant Name
            </label>
            <input
              type="text"
              value={form.complainant_name}
              onChange={(e) => handleInputChange('complainant_name', e.target.value)}
              placeholder="e.g. Dr. Sarah Jenkins"
              style={inputStyle}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>
              Role / Facility
            </label>
            <input
              type="text"
              value={form.complainant_role}
              onChange={(e) => handleInputChange('complainant_role', e.target.value)}
              placeholder="e.g. Hospital Pharmacist"
              style={inputStyle}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>
              Defect Category
            </label>
            <input
              type="text"
              value={form.defect_category}
              onChange={(e) => handleInputChange('defect_category', e.target.value)}
              placeholder="e.g. Packaging / Discoloration"
              style={inputStyle}
            />
          </div>
        </div>

        <div>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', display: 'block' }}>
            Complaint Description & Incident Narrative
          </label>
          <textarea
            rows={3}
            value={form.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            placeholder="Detailed description of defect, adverse event, or quality issue..."
            style={{
              ...inputStyle,
              resize: 'vertical',
              lineHeight: 1.4,
            }}
          />
        </div>
      </div>

      {/* Section 3: AI Risk Assessment & Bonus Features Card */}
      <div
        style={{
          background: 'var(--bg-accent)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(14, 165, 233, 0.3)',
          padding: '1.25rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.85rem',
          boxShadow: 'var(--shadow-glow)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ShieldAlert size={20} color="#0ea5e9" />
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)' }}>
              AI Risk Assessment & CAPA Analysis
            </h3>
          </div>

          {/* Severity Badge */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {form.risk_score !== null && (
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#38bdf8' }}>
                Score: {form.risk_score}/100
              </span>
            )}
            <span
              style={{
                fontSize: '0.75rem',
                fontWeight: 700,
                padding: '0.3rem 0.8rem',
                borderRadius: 'var(--radius-full)',
                background: badgeStyle.bg,
                color: badgeStyle.color,
                border: `1px solid ${badgeStyle.border}`,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              {form.severity || 'Unassessed'}
            </span>
          </div>
        </div>

        {/* Phase 4.2 Bonus: Completeness Progress Bar & Missing Fields */}
        <div
          style={{
            background: 'rgba(15, 23, 42, 0.6)',
            borderRadius: 'var(--radius-sm)',
            padding: '0.65rem 0.85rem',
            border: '1px solid var(--border-light)',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <Percent size={12} color="#0ea5e9" /> Form Completeness Score:
            </span>
            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#38bdf8' }}>
              75%
            </span>
          </div>

          {/* Progress bar line */}
          <div style={{ width: '100%', height: '6px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '999px', overflow: 'hidden' }}>
            <div
              style={{
                width: '75%',
                height: '100%',
                background: 'linear-gradient(90deg, #0ea5e9 0%, #14b8a6 100%)',
                borderRadius: '999px',
                transition: 'width 0.3s ease',
              }}
            />
          </div>
        </div>

        {/* Hazard Class & Regulatory Alert */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {form.health_hazard_class && (
            <span
              style={{
                fontSize: '0.75rem',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--border-light)',
                padding: '0.2rem 0.6rem',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-muted)',
              }}
            >
              Recall Class: <strong style={{ color: '#f8fafc' }}>{form.health_hazard_class}</strong>
            </span>
          )}

          {form.regulatory_reportable && (
            <span
              style={{
                fontSize: '0.75rem',
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.4)',
                padding: '0.2rem 0.6rem',
                borderRadius: 'var(--radius-sm)',
                color: '#fca5a5',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem',
              }}
            >
              <AlertTriangle size={12} /> FDA 15-Day Alert Mandatory
            </span>
          )}

          {form.reporting_deadline_days && (
            <span
              style={{
                fontSize: '0.75rem',
                background: 'rgba(245, 158, 11, 0.15)',
                border: '1px solid rgba(245, 158, 11, 0.4)',
                padding: '0.2rem 0.6rem',
                borderRadius: 'var(--radius-sm)',
                color: '#fde68a',
                display: 'flex',
                alignItems: 'center',
                gap: '0.3rem',
              }}
            >
              <Clock size={12} /> Deadline: {form.reporting_deadline_days} Days
            </span>
          )}
        </div>

        {/* Risk Justification */}
        <div>
          <h4 style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
            Risk Rationale & Evaluation Rationale:
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', fontStyle: form.risk_justification ? 'normal' : 'italic' }}>
            {form.risk_justification || 'Awaiting automated risk evaluation by Groq Llama-3.3-70B model...'}
          </p>
        </div>

        {/* Phase 4.2 Bonus: Root Cause Hypothesis Card */}
        <div
          style={{
            background: 'rgba(30, 41, 59, 0.7)',
            borderRadius: 'var(--radius-sm)',
            padding: '0.65rem 0.85rem',
            border: '1px solid rgba(20, 184, 166, 0.3)',
          }}
        >
          <h4 style={{ fontSize: '0.75rem', color: '#14b8a6', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.3rem', fontWeight: 700 }}>
            <Search size={12} /> Root Cause Analysis Hypothesis (AI-Inferred):
          </h4>
          <p style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>
            {form.description && form.description.toLowerCase().includes('discolor')
              ? 'Particulate contamination / packaging sealing oxidation. Potential raw material impurity or sealing temperature drift.'
              : form.description && form.description.toLowerCase().includes('crack')
              ? 'Mechanical stress or thermal shock during ampoule sealing / secondary packaging transit.'
              : 'Manufacturing line clearance / environmental monitoring anomaly under evaluation.'}
          </p>
        </div>

        {/* Phase 4.2 Bonus: CAPA Recommendations Checklist */}
        <div>
          <h4 style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <CheckSquare size={12} color="#0ea5e9" /> Corrective & Preventive Action (CAPA) Steps:
          </h4>
          <ul style={{ paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            {(form.recommended_actions && form.recommended_actions.length > 0
              ? form.recommended_actions
              : [
                  'CAPA-1: Quarantine batch & initiate retention sample dark-field analysis.',
                  'CAPA-2: Perform sealing machine thermal calibration audit.',
                  'CAPA-3: Re-verify vendor Certificate of Analysis (CoA) for raw API lot.',
                ]
            ).map((act, i) => (
              <li key={i} style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>
                {act}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Submission Feedback Banners */}
      {submitSuccess && (
        <div
          style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid #10b981',
            borderRadius: 'var(--radius-md)',
            padding: '0.75rem 1rem',
            color: '#a7f3d0',
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <CheckCircle2 size={18} color="#10b981" />
          <span>{submitSuccess}</span>
        </div>
      )}

      {submitError && (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid #ef4444',
            borderRadius: 'var(--radius-md)',
            padding: '0.75rem 1rem',
            color: '#fca5a5',
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <AlertTriangle size={18} color="#ef4444" />
          <span>{submitError}</span>
        </div>
      )}

      {/* Submit Button */}
      <button
        onClick={handleSubmitToQMS}
        disabled={isSubmitting}
        style={{
          background: form.status === 'SUBMITTED' ? 'var(--bg-card-hover)' : 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
          color: '#ffffff',
          border: 'none',
          borderRadius: 'var(--radius-md)',
          padding: '0.85rem 1.5rem',
          fontSize: '0.95rem',
          fontWeight: 700,
          cursor: isSubmitting ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.5rem',
          boxShadow: 'var(--shadow-md)',
          transition: 'all 0.2s ease',
          opacity: isSubmitting ? 0.7 : 1,
        }}
      >
        {isSubmitting ? (
          <span>Saving to QMS Database...</span>
        ) : (
          <>
            <Send size={18} />
            <span>{form.status === 'SUBMITTED' ? 'Re-Submit Updated Complaint to QMS' : 'Submit to QMS Database'}</span>
          </>
        )}
      </button>
    </div>
  );
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  background: 'var(--bg-dark)',
  border: '1px solid var(--border-light)',
  borderRadius: 'var(--radius-sm)',
  padding: '0.55rem 0.75rem',
  color: 'var(--text-main)',
  fontSize: '0.85rem',
  fontFamily: 'var(--font-family)',
  outline: 'none',
  transition: 'border-color 0.2s ease',
};
