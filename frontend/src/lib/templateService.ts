export class TemplateService {
  private baseUrl: string;

  constructor(baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  private authHeaders() {
    if (typeof window === 'undefined') return { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('access_token');
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;
    return headers;
  }

  async generateExcel(templateType: string, data: any): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/generate-excel/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.authHeaders(),
      },
      body: JSON.stringify({ template_type: templateType, data }),
    });

    if (!response.ok) {
      throw new Error(`Error generating Excel: ${response.statusText}`);
    }

    return await response.blob();
  }

  async generatePDF(templateType: string, data: any): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/generate-pdf/`, {
      method: 'POST',
      headers: {
        ...this.authHeaders(),
      },
      body: JSON.stringify({ template_type: templateType, data }),
    });

    if (!response.ok) {
      throw new Error(`Error generating PDF: ${response.statusText}`);
    }

    return await response.blob();
  }

  downloadFile(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  async generateFromTemplate(templateId: string | number, data: any): Promise<Blob> {
    const id = encodeURIComponent(String(templateId));
    const response = await fetch(`${this.baseUrl}/api/templates/${id}/generate/`, {
      method: 'POST',
      headers: this.authHeaders(),
      body: JSON.stringify({ data }),
    });

    if (!response.ok) {
      throw new Error(`Error generating from template: ${response.statusText}`);
    }

    return await response.blob();
  }

  async generateFromMaintenance(templateId: string | number, maintenanceId: number): Promise<Blob> {
    // convenience endpoint that your backend can implement: /api/templates/{id}/generate/?maintenance_id=
    const url = new URL(`${this.baseUrl}/api/templates/${encodeURIComponent(String(templateId))}/generate/`);
    url.searchParams.set('maintenance_id', String(maintenanceId));

    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: this.authHeaders(),
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      throw new Error(`Error generating from maintenance: ${response.statusText}`);
    }

    return await response.blob();
  }
}
