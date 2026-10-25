import ImageGrid from "@/app/(auth)/_components/ImageGrid";
import SignUpForm from "@/app/(auth)/signup/_components/SignUpForm";
export default function SingUp() {
  return (
    <div className="flex h-full">
      <ImageGrid />
      <SignUpForm />
    </div>
  );
}
