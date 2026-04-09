import { useNavigate } from "react-router-dom";
import { ShieldOff } from "lucide-react";

export const UnauthorizedPage = () => {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <ShieldOff size={48} className="text-gray-400 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-800 mx-auto mb-2">
          Access Denied
        </h1>
        <p className="text-gray-500 mb-6">
          You don't have the permission to view this page
        </p>
        <button
          onClick={() => navigate("/")}
          className="bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors "
        >
          Back to Dashboard
        </button>
      </div>
    </div>
  );
};
