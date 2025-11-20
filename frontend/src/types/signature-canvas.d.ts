declare module 'react-signature-canvas' {
  import { Component } from 'react';

  export interface SignatureCanvasProps {
    canvasProps?: React.CanvasHTMLAttributes<HTMLCanvasElement>;
    clearOnResize?: boolean;
  }

  export default class SignatureCanvas extends Component<SignatureCanvasProps> {
    clear(): void;
    toDataURL(type?: string, encoderOptions?: number): string;
    fromDataURL(dataURL: string): void;
    isEmpty(): boolean;
  }
}