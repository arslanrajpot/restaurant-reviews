type LogoProps = {
  className?: string;
  /** "color" for use on light backgrounds, "light" for use on the dark teal sidebar */
  variant?: "color" | "light";
};

export default function Logo({ className = "", variant = "color" }: LogoProps) {
  const isLight = variant === "light";
  const badgeFill = isLight ? "#ffffff" : "var(--color-theme)";
  const bubbleStroke = isLight ? "var(--color-theme)" : "#ffffff";
  const reviewColor = isLight ? "#ffffff" : "#1f2937";
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
      <rect x="4" y="6" width="60" height="60" rx="16" fill={badgeFill} />
      <rect
        x="16"
        y="18"
        width="36"
        height="24"
        rx="8"
        fill="none"
        stroke={bubbleStroke}
        strokeWidth="3"
      />
      <polygon points="24,42 18,52 32,42" fill={bubbleStroke} />
      <path
        d="M20,30 L26,30 L29,22 L33,38 L37,30 L46,30"
        fill="none"
        stroke={pulseColor}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <text
        x="78"
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
