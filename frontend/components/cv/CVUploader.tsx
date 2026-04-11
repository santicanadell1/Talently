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
        w-full h-full min-h-[220px] rounded-xl border cursor-pointer
        transition-all duration-200
        ${isDragging
          ? "border-[#E8192C]/50 bg-[#E8192C]/5"
          : selectedFile
            ? "border-[#E8192C]/30 bg-[#111111]"
            : "border-white/8 bg-[#111111] hover:border-white/15"
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
          <div className="w-10 h-10 rounded-lg bg-[#E8192C]/10 flex items-center justify-center">
            <FileText className="w-5 h-5 text-[#E8192C]" />
          </div>
          <div className="text-center">
            <p className="text-[#F1F5F9] text-sm font-medium">{selectedFile.name}</p>
            <p className="text-[#444] text-xs mt-1">
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB · clic para cambiar
            </p>
          </div>
        </>
      ) : (
        <>
          <div className="w-10 h-10 rounded-lg bg-white/4 flex items-center justify-center">
            <Upload className="w-4 h-4 text-[#555]" />
          </div>
          <div className="text-center">
            <p className="text-[#888] text-sm">Arrastrá tu CV aquí</p>
            <p className="text-[#444] text-xs mt-1">o hacé clic para seleccionarlo</p>
          </div>
          <span className="text-[#333] text-xs border border-white/6 rounded-full px-3 py-1 tracking-widest uppercase">
            PDF · máx. 5MB
          </span>
        </>
      )}
    </div>
  );
}
