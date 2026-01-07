// src/components/shared/Loading.tsx
import React from "react";

interface LoadingProps {
  message?: string;
}

const Loading: React.FC<LoadingProps> = ({ message = "Chargement..." }) => {
  return (
    <div className="text-sm opacity-80">
      {message}
    </div>
  );
};

export default Loading;

