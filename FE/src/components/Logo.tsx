import iconImg from "@/assets/images/logo-icon.png";

type LogoProps = {
  className?: string;
  /** "color" for use on light backgrounds, "light" for use on the dark teal sidebar */
  variant?: "color" | "light";
};

export default function Logo({ className = "", variant = "color" }: LogoProps) {
  const reviewColor = variant === "light" ? "#ffffff" : "#1f2937";
  const pulseColor = "var(--button-theme)";

  return (
    <svg
      viewBox="0 0 330 72"
      className={className}
      role="img"
      aria-label="ReviewPulse"
      xmlns="http://www.w3.org/2000/svg"
    >
      <title>ReviewPulse</title>
      <image href={iconImg.src} x="2" y="4" width="64" height="64" />
      <text
        x="80"
        y="47"
        fontFamily="'Segoe UI', Arial, Helvetica, sans-serif"
        fontWeight="700"
        fontSize="30"
      >
        <tspan fill={reviewColor}>Review</tspan>
        <tspan fill={pulseColor}>Pulse</tspan>
      </text>
    </svg>
  );
}
