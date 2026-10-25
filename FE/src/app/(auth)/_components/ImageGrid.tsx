import Image from "next/image";
import LoginImage from "@/assets/images/login_image.jpg";

export default function ImageGrid() {
  return (
    <div className="w-1/3 h-full relative">
      <Image
        src={LoginImage}
        layout="fill"
        objectFit="cover"
        className="absolute inset-0"
        alt="Login Image"
      />
    </div>
  );
}