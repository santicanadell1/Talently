"use client";

import { useRef, useState } from "react";

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
        flex flex-col items-center justify-center gap-3
        w-full h-48 rounded-xl border-2 border-dashed cursor-pointer
        transition-colors duration-200
        ${isDragging
          ? "border-[#B11623] bg-[#B11623]/10"
          : "border-[#3a3d4a] bg-[#292C37] hover:border-[#B11623]/60"
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
          <span className="text-3xl">📄</span>
          <p className="text-[#F0F0F0] font-medium text-sm">{selectedFile.name}</p>
          <p className="text-[#CCCCCC] text-xs">
            {(selectedFile.size / 1024 / 1024).toFixed(2)} MB — clic para cambiar
          </p>
        </>
      ) : (
        <>
          <span className="text-3xl">⬆️</span>
          <p className="text-[#F0F0F0] font-medium text-sm">
            Arrastrá tu CV o hacé clic para seleccionarlo
          </p>
          <p className="text-[#CCCCCC] text-xs">Solo PDF · Máximo 5MB</p>
        </>
      )}
    </div>
  );
}
