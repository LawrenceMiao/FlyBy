import { ComponentPropsWithoutRef, ReactNode } from "react";
import { cn } from "@/lib/utils";

interface BentoGridProps extends ComponentPropsWithoutRef<"div"> {
  children: ReactNode;
  className?: string;
}

interface BentoCardProps extends ComponentPropsWithoutRef<"div"> {
  value: string | number | null;
  description: string;
  className?: string;
}

const BentoGrid = ({ children, className, ...props }: BentoGridProps) => {
  return (
    <div
      className={cn(
        "grid w-full auto-rows-[13rem] grid-cols-5 gap-4",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
};

const BentoCard = ({ title, value, description, className, ...props }: BentoCardProps) => (
  <div
    className={cn(
      "group relative col-span-3 flex flex-col justify-between overflow-hidden rounded-xl",
      "bg-background [box-shadow:0_0_0_1px_rgba(0,0,0,.03),0_2px_4px_rgba(0,0,0,.05),0_12px_24px_rgba(0,0,0,.05)]",
      className,
    )}
    {...props}
  >
    <div className="pointer-events-none z-10 flex flex-col gap-1 p-6">
      <h3 className="text-[2rem] font-semibold text-[#0f4592] leading-tight mb-4">{title}</h3>
      <h3 className="text-[4rem] md:text-[5rem] font-semibold text-[#0f4592]">{value}</h3>
      <p className="max-w-lg text-neutral-500 text-[1.25rem]">{description}</p>
    </div>
  </div>
);

export { BentoCard, BentoGrid };