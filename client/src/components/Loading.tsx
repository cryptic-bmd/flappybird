type RotatingArcLoaderProps = {
  size?: number;
  speedSec?: number;
  overlay?: boolean;
  message?: string;
};

export default function RotatingArcLoader({
  size = 140,
  speedSec = 3,
  overlay = true,
  message = "",
}: RotatingArcLoaderProps) {
  const colors = [
    "#009e80", // dark teal
    "#00d1a0", // medium teal
    "#00e6ac", // bright teal
  ];

  const gradientStops = colors
    .map((c, i) => `${c} ${i * (160 / colors.length)}deg`)
    .join(", ");

  return (
    <div
      className={`${overlay ? "fixed inset-0 flex items-center justify-center bg-layer2 z-50" : "inline-flex"} flex-col gap-4`}
    >
      <div
        className="relative flex items-center justify-center"
        style={{ width: size, height: size }}
      >
        <div
          className="absolute rounded-full"
          style={{
            width: size,
            height: size,
            background: `conic-gradient(from 90deg, ${gradientStops}, transparent 200deg)`,
            filter: "blur(6px)",
            animation: `rotate ${speedSec}s linear infinite`,
            maskImage: "radial-gradient(circle, transparent calc(50% - 4px), black calc(50% - 3px))",
            WebkitMaskImage: "radial-gradient(circle, transparent calc(50% - 4px), black calc(50% - 3px))",
          }}
        />
      </div>

      {message && (
        <span className="text-white text-sm font-medium tracking-wide">{message}</span>
      )}

      <style>
        {`
          @keyframes rotate {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
}
