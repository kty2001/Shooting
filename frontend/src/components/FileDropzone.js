import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaUpload } from 'react-icons/fa';

const FileDropzone = ({ onFileDrop, acceptedFileTypes, fileTypeDescription }) => {
  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onFileDrop(acceptedFiles[0]);
      }
    },
    [onFileDrop]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedFileTypes,
    multiple: false,
  });

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-md p-xl flex flex-col items-center justify-center
        cursor-pointer transition-all duration-fast mb-xs mt-md h-[660px] w-full
        ${isDragActive ? 'border-primary bg-primary/10' : 'border-border bg-surface'}
        hover:border-primary hover:bg-primary/10
      `}
    >
      <input {...getInputProps()} />
      <FaUpload className="text-5xl text-primary mb-md" />
      <p className="text-textPrimary text-center mb-md">
        {isDragActive
          ? '파일을 여기에 놓으세요'
          : '파일을 드래그 앤 드롭하거나 클릭하여 선택하세요'}
      </p>
      <p className="text-textSecondary text-sm text-center">
        {fileTypeDescription}
      </p>
    </div>
  );
};

export default FileDropzone; 