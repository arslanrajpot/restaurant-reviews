import ImageGrid from "@/app/(auth)/_components/ImageGrid";
import ForgetPasswordForm from "@/app/(auth)/forget_password/_components/ForgetPasswordForm";
export default function ForgetPassword() {

  return (
    <div className="flex h-screen">
        <ImageGrid />
        <ForgetPasswordForm />
    </div>
  );
}
