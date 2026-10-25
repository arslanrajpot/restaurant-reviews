import ImageGrid from "@/app/(auth)/_components/ImageGrid";
import LoginForm from "@/app/(auth)/login/_components/LoginForm";
export default function Login() {
  return (
    <div className="flex h-full">
      <ImageGrid />
      <LoginForm />
    </div>
  );
}
