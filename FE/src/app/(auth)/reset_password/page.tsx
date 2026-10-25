import { Suspense } from "react";
import ImageGrid from "@/app/(auth)/_components/ImageGrid";
import ResetPasswordForm from "@/app/(auth)/reset_password/_components/ResetPasswordForm";
export default function ResetPassword() {

  return (
    <Suspense fallback={<p>Loading...</p>}>
      <div className="flex h-screen">
        <ImageGrid />
        <ResetPasswordForm />
      </div>
    </Suspense>
  );
}
