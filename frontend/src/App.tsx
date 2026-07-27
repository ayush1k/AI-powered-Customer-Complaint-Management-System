import React, { useState, useEffect } from 'react';
import { useAppDispatch } from './store';
import { setEntireState, resetForm } from './store/formSlice';
import { addMessage, clearChat } from './store/chatSlice';
import { ComplaintForm, CopilotPanel } from './components';
import {
  ShieldCheck,
  Cpu,
  RefreshCw,
  FileCheck2,
  Database,
  Layers,
} from 'lucide-react';
import axios from 'axios';

export const App: React.FC = () => {
  const dispatch = useAppDispatch();
  const [backendHealth, setBackendHealth] = useState<'healthy' | 'offline' | 'checking'>('checking');

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    setBackendHealth('checking');
    try {
      const res = await axios.get('/api/health');
      if (res.data && res.data.status === 'healthy') {
        setBackendHealth('healthy');
      } else {
        setBackendHealth('offline');
      }
    } catch {
      setBackendHealth('offline');
    }
  };

  const loadSample1 = () => {
    dispatch(
      setEntireState({
        formState: {
          product_name: 'CardioShield',
          strength: '10mg Tablets',
          batch_number: 'LOT-9921A',
          manufacture_date: '2025-01-15',
          expiry_date: '2027-11-30',
          complaint_quantity: '15 bottles / 1,500 tablets',
          description: 'Visible black specks and dark discoloration embedded inside sealed blister foil. Patient experienced mild nausea.',
          complainant_name: 'Dr. Sarah Jenkins',
          complainant_role: 'Clinical Director of Pharmacy',
          complainant_contact: 'dr.sarah.jenkins@stjudehospital.org',
          defect_category: 'Contamination / Discoloration',
          status: 'IN_REVIEW',
          complaint_id: 'CMP-2026-0042',
        },
        riskState: {
          severity: 'Major',
          risk_justification: 'Particulate matter in oral unit dose tablets; mild nausea reported by hospital ward.',
          recommended_next_actions: [
            'Quarantine lot LOT-9921A immediately',
            'File FDA 15-Day Alert Report',
            'Initiate retention sample laboratory inspection',
          ],
          risk_score: 78,
          health_hazard_class: 'CLASS_II',
          regulatory_reportable: true,
          reporting_deadline_days: 15,
        },
      })
    );

    dispatch(
      addMessage({
        sender: 'copilot',
        message: 'Loaded sample complaint: **CardioShield 10mg Tablets (Lot LOT-9921A)**. Form and risk score (78) auto-populated.',
        tool_used: 'sample_loader',
      })
    );
  };

  const loadSample2 = () => {
    dispatch(
      setEntireState({
        formState: {
          product_name: 'NeuroCalm Injection',
          strength: '5mg/mL Solution',
          batch_number: 'BATCH-88402X',
          manufacture_date: '2025-06-10',
          expiry_date: '2026-12-31',
          complaint_quantity: '2 ampoules',
          description: 'Hairline crack along neck of glass ampoule resulting in fluid leakage inside carton.',
          complainant_name: 'Mark Stevens',
          complainant_role: 'Patient',
          complainant_contact: 'mstevens@example.com',
          defect_category: 'Packaging Integrity Failure',
          status: 'IN_REVIEW',
          complaint_id: 'CMP-2026-0089',
        },
        riskState: {
          severity: 'Critical',
          risk_justification: 'Sterility breach in parenteral injectable dosage form poses serious microbial safety hazard.',
          recommended_next_actions: [
            'Issue immediate batch hold on BATCH-88402X',
            'Perform glass container inspection audit',
            'File FDA MedWatch Safety Report',
          ],
          risk_score: 92,
          health_hazard_class: 'CLASS_I',
          regulatory_reportable: true,
          reporting_deadline_days: 15,
        },
      })
    );

    dispatch(
      addMessage({
        sender: 'copilot',
        message: 'Loaded sample complaint: **NeuroCalm Injection (Batch BATCH-88402X)**. Form and Critical Risk score (92) auto-populated.',
        tool_used: 'sample_loader',
      })
    );
  };

  const handleClearAll = () => {
    dispatch(resetForm());
    dispatch(clearChat());
    dispatch(
      addMessage({
        sender: 'copilot',
        message: 'Form and chat cleared. Ready for new complaint intake or file upload.',
        tool_used: 'system',
      })
    );
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'var(--bg-dark)',
        color: 'var(--text-main)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Top Navbar */}
      <header
        style={{
          background: 'var(--bg-card)',
          borderBottom: '1px solid var(--border-light)',
          padding: '0.85rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div
            style={{
              background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
              padding: '0.5rem',
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              alignItems: 'center',
              boxShadow: 'var(--shadow-glow)',
            }}
          >
            <ShieldCheck size={26} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#f8fafc' }}>
                AIVOA
              </h1>
              <span
                style={{
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  background: 'rgba(14, 165, 233, 0.2)',
                  color: '#38bdf8',
                  padding: '0.15rem 0.5rem',
                  borderRadius: 'var(--radius-full)',
                  border: '1px solid rgba(14, 165, 233, 0.4)',
                }}
              >
                v1.0 Enterprise
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              AI-Powered Pharmaceutical Customer Complaint Management & Risk Assessment
            </p>
          </div>
        </div>

        {/* Action Controls & Indicators */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* Sample Loaders */}
          <button onClick={loadSample1} style={navBtnStyle} title="Load Discolored Tablet Sample">
            <FileCheck2 size={14} color="#38bdf8" /> Sample 1 (Tablet)
          </button>

          <button onClick={loadSample2} style={navBtnStyle} title="Load Ampoule Defect Sample">
            <Layers size={14} color="#14b8a6" /> Sample 2 (Ampoule)
          </button>

          <button onClick={handleClearAll} style={{ ...navBtnStyle, opacity: 0.8 }} title="Reset form and chat">
            <RefreshCw size={14} /> Reset
          </button>

          {/* Model Badge */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              fontSize: '0.75rem',
              background: 'var(--bg-accent)',
              padding: '0.35rem 0.75rem',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid rgba(14, 165, 233, 0.3)',
            }}
          >
            <Cpu size={14} color="#38bdf8" />
            <span style={{ color: '#cbd5e1', fontWeight: 600 }}>Groq Llama-3.3-70B</span>
          </div>

          {/* Backend Status Indicator */}
          <div
            onClick={checkHealth}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              fontSize: '0.75rem',
              background: 'var(--bg-dark)',
              padding: '0.35rem 0.75rem',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-light)',
              cursor: 'pointer',
            }}
            title="Click to re-check backend status"
          >
            <Database size={14} color={backendHealth === 'healthy' ? '#10b981' : '#ef4444'} />
            <span style={{ color: backendHealth === 'healthy' ? '#a7f3d0' : '#fca5a5', fontWeight: 600 }}>
              {backendHealth === 'healthy' ? 'API Online' : 'API Offline'}
            </span>
          </div>
        </div>
      </header>

      {/* Main Dual-Panel Grid */}
      <main
        style={{
          flex: 1,
          padding: '1.25rem 1.5rem',
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)',
          gap: '1.25rem',
          maxWidth: '1800px',
          width: '100%',
          margin: '0 auto',
        }}
      >
        {/* Left Panel: Reactive Form */}
        <section style={{ minWidth: 0 }}>
          <ComplaintForm />
        </section>

        {/* Right Panel: Copilot Chat & Upload */}
        <section style={{ minWidth: 0 }}>
          <CopilotPanel />
        </section>
      </main>
    </div>
  );
};

const navBtnStyle: React.CSSProperties = {
  background: 'var(--bg-dark)',
  border: '1px solid var(--border-light)',
  color: 'var(--text-main)',
  borderRadius: 'var(--radius-sm)',
  padding: '0.4rem 0.75rem',
  fontSize: '0.75rem',
  fontWeight: 600,
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  gap: '0.35rem',
  transition: 'all 0.2s ease',
};

export default App;
