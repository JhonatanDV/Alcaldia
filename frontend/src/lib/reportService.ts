export class ReportService {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  private getToken(): string {
    if (typeof window === 'undefined') return '';
    return localStorage.getItem('access_token') || localStorage.getItem('token') || '';
  }

  async generateReport(maintenanceId: number, format: 'pdf' | 'excel' | 'image'): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/reports/generate/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`,
      },
      body: JSON.stringify({ maintenance_id: maintenanceId, format }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: response.statusText }));
      throw new Error(error.error || 'Error generando reporte');
    }

    return response.blob();
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
}

export const reportService = new ReportService();
