import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export interface FormState {
  complaint_id: string | null;
  product_name: string;
  strength: string;
  batch_number: string;
  manufacture_date: string;
  expiry_date: string;
  complaint_quantity: string;
  description: string;
  complainant_name: string;
  complainant_role: string;
  complainant_contact: string;
  defect_category: string;
  status: string;

  // Risk Assessment
  severity: 'Critical' | 'Major' | 'Minor' | null;
  risk_justification: string;
  recommended_actions: string[];
  risk_score: number | null;
  health_hazard_class: 'CLASS_I' | 'CLASS_II' | 'CLASS_III' | null;
  regulatory_reportable: boolean;
  reporting_deadline_days: number | null;
}

const initialState: FormState = {
  complaint_id: null,
  product_name: '',
  strength: '',
  batch_number: '',
  manufacture_date: '',
  expiry_date: '',
  complaint_quantity: '',
  description: '',
  complainant_name: '',
  complainant_role: '',
  complainant_contact: '',
  defect_category: '',
  status: 'DRAFT',

  severity: null,
  risk_justification: '',
  recommended_actions: [],
  risk_score: null,
  health_hazard_class: null,
  regulatory_reportable: false,
  reporting_deadline_days: null,
};

export const formSlice = createSlice({
  name: 'form',
  initialState,
  reducers: {
    updateFormField: (
      state,
      action: PayloadAction<{ field: keyof FormState; value: any }>
    ) => {
      const { field, value } = action.payload;
      (state as any)[field] = value;
    },
    updateFormState: (state, action: PayloadAction<Partial<FormState>>) => {
      return { ...state, ...action.payload };
    },
    updateRiskState: (
      state,
      action: PayloadAction<{
        severity?: 'Critical' | 'Major' | 'Minor' | null;
        risk_justification?: string;
        recommended_next_actions?: string[];
        risk_score?: number | null;
        health_hazard_class?: 'CLASS_I' | 'CLASS_II' | 'CLASS_III' | null;
        regulatory_reportable?: boolean;
        reporting_deadline_days?: number | null;
      }>
    ) => {
      const r = action.payload;
      if (r.severity !== undefined) state.severity = r.severity;
      if (r.risk_justification !== undefined) state.risk_justification = r.risk_justification;
      if (r.recommended_next_actions !== undefined) state.recommended_actions = r.recommended_next_actions;
      if (r.risk_score !== undefined) state.risk_score = r.risk_score;
      if (r.health_hazard_class !== undefined) state.health_hazard_class = r.health_hazard_class;
      if (r.regulatory_reportable !== undefined) state.regulatory_reportable = r.regulatory_reportable;
      if (r.reporting_deadline_days !== undefined) state.reporting_deadline_days = r.reporting_deadline_days;
    },
    setEntireState: (
      state,
      action: PayloadAction<{
        formState?: Partial<FormState>;
        riskState?: any;
      }>
    ) => {
      const { formState, riskState } = action.payload;
      if (formState) {
        Object.assign(state, formState);
      }
      if (riskState) {
        if (riskState.severity) state.severity = riskState.severity;
        if (riskState.risk_justification) state.risk_justification = riskState.risk_justification;
        if (riskState.recommended_next_actions) state.recommended_actions = riskState.recommended_next_actions;
        if (riskState.risk_score !== undefined) state.risk_score = riskState.risk_score;
        if (riskState.health_hazard_class) state.health_hazard_class = riskState.health_hazard_class;
        if (riskState.regulatory_reportable !== undefined) state.regulatory_reportable = riskState.regulatory_reportable;
        if (riskState.reporting_deadline_days !== undefined) state.reporting_deadline_days = riskState.reporting_deadline_days;
      }
    },
    resetForm: () => initialState,
  },
});

export const {
  updateFormField,
  updateFormState,
  updateRiskState,
  setEntireState,
  resetForm,
} = formSlice.actions;

export default formSlice.reducer;
