"use client";

import { useRef, useState } from "react";
import { Upload, FileText } from "lucide-react";

interface CVUploaderProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
}

export function CVUploader({ onFileSelect, selectedFile }: CVUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file?.type === "application/pdf") onFileSelect(file);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  return (
    <div
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`
        relative flex flex-col items-center justify-center gap-4
        w-full h-full min-h-[220px] rounded-2xl border-2 border-dashed cursor-pointer
        transition-all duration-200
        ${isDragging
          ? "border-[#B11623] bg-[#B11623]/10 scale-[1.01]"
          : selectedFile
            ? "border-[#B11623]/60 bg-[#B11623]/5"
            : "border-[#3a3d4a] bg-[#1a1d27] hover:border-[#B11623]/50 hover:bg-[#B11623]/5"
        }
      `}
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={handleChange}
      />

      {selectedFile ? (
        <>
          <div className="w-12 h-12 rounded-xl bg-[#B11623]/20 flex items-center justify-center">
            <FileText className="w-6 h-6 text-[#B11623]" />
          </div>
          <div className="text-center">
            <p className="text-[#F0F0F0] font-medium text-sm">{selectedFile.name}</p>
            <p className="text-[#CCCCCC] text-xs mt-1">
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB · clic para cambiar
            </p>
          </div>
        </>
      ) : (
        <>
          <div className="w-12 h-12 rounded-xl bg-[#292C37] flex items-center justify-center">
            <Upload className="w-5 h-5 text-[#CCCCCC]" />
          </div>
          <div className="text-center">
            <p className="text-[#F0F0F0] font-medium text-sm">Arrastrá tu CV aquí</p>
            <p className="text-[#CCCCCC] text-xs mt-1">o hacé clic para seleccionarlo</p>
          </div>
          <span className="text-[#CCCCCC]/50 text-xs border border-[#3a3d4a] rounded-full px-3 py-1">
            PDF · máx. 5MB
          </span>
        </>
      )}
    </div>
  );
}
