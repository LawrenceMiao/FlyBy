import { cn } from "@/lib/utils";
// import { Button } from "@/components/ui/button";
import { BentoGrid } from "@/components/magicui/bento-grid";


export default function Homepage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 pt-4">
      <h1 className="text-4xl font-bold mb-4">TACO</h1>

      <BentoGrid className="p-8 pt-2">
        <div
          className={cn(
            "group relative col-span-3 flex flex-col justify-between overflow-hidden rounded-xl",
            // light styles
            "bg-background [box-shadow:0_0_0_1px_rgba(0,0,0,.03),0_2px_4px_rgba(0,0,0,.05),0_12px_24px_rgba(0,0,0,.05)]",
            // dark styles
            "transform-gpu dark:bg-background dark:[border:1px_solid_rgba(255,255,255,.1)] dark:[box-shadow:0_-20px_80px_-20px_#ffffff1f_inset]",
            
            "lg:row-start-1 lg:row-end-4 lg:col-start-1 lg:col-end-4",
          )}
        >
          <div className="pointer-events-none z-10 flex flex-col gap-1 p-6 ">
            {/* <Icon className="h-12 w-12 origin-left transform-gpu text-neutral-700 transition-all duration-300 ease-in-out group-hover:scale-75" /> */}
            <h3 className="text-xl font-semibold text-neutral-700 dark:text-neutral-300">
              Miranda
            </h3>
            <p className="max-w-lg text-neutral-400">Miranda</p>
          </div>
        </div>

        <div
          className={cn(
            "group relative col-span-3 flex flex-col justify-between overflow-hidden rounded-xl",
            // light styles
            "bg-background [box-shadow:0_0_0_1px_rgba(0,0,0,.03),0_2px_4px_rgba(0,0,0,.05),0_12px_24px_rgba(0,0,0,.05)]",
            // dark styles
            "transform-gpu dark:bg-background dark:[border:1px_solid_rgba(255,255,255,.1)] dark:[box-shadow:0_-20px_80px_-20px_#ffffff1f_inset]",
            
            "lg:row-start-1 lg:row-end-3 lg:col-start-4 lg:col-end-4",
          )}
        >
          <div className="pointer-events-none z-10 flex flex-col gap-1 p-6 ">
            {/* <Icon className="h-12 w-12 origin-left transform-gpu text-neutral-700 transition-all duration-300 ease-in-out group-hover:scale-75" /> */}
            <h3 className="text-[5rem] font-semibold text-neutral-700 dark:text-neutral-300">
              lala
            </h3>
            <p className="max-w-lg text-neutral-500 text-[1.25rem]">lala i need more data</p>
          </div>
        </div>

        <div
          className={cn(
            "group relative col-span-3 flex flex-col justify-between overflow-hidden rounded-xl",
            // light styles
            "bg-background [box-shadow:0_0_0_1px_rgba(0,0,0,.03),0_2px_4px_rgba(0,0,0,.05),0_12px_24px_rgba(0,0,0,.05)]",
            // dark styles
            "transform-gpu dark:bg-background dark:[border:1px_solid_rgba(255,255,255,.1)] dark:[box-shadow:0_-20px_80px_-20px_#ffffff1f_inset]",
            
            "lg:row-start-1 lg:row-end-2 lg:col-start-5 lg:col-end-5",
          )}
        >
          <div className="pointer-events-none z-10 flex flex-col gap-1 p-6 ">
            {/* <Icon className="h-12 w-12 origin-left transform-gpu text-neutral-700 transition-all duration-300 ease-in-out group-hover:scale-75" /> */}
            <h3 className="text-[5rem] font-semibold text-neutral-700 dark:text-neutral-300">
              55
            </h3>
            <p className="max-w-lg text-neutral-500 text-[1.25rem]">pieces of trash found</p>
          </div>
        </div>

        <div
          className={cn(
            "group relative col-span-3 flex flex-col justify-between overflow-hidden rounded-xl",
            // light styles
            "bg-background [box-shadow:0_0_0_1px_rgba(0,0,0,.03),0_2px_4px_rgba(0,0,0,.05),0_12px_24px_rgba(0,0,0,.05)]",
            // dark styles
            "transform-gpu dark:bg-background dark:[border:1px_solid_rgba(255,255,255,.1)] dark:[box-shadow:0_-20px_80px_-20px_#ffffff1f_inset]",
            
            "lg:row-start-2 lg:row-end-3 lg:col-start-5 lg:col-end-5",
          )}
        >
          <div className="pointer-events-none z-10 flex flex-col gap-1 p-6 ">
            {/* <Icon className="h-12 w-12 origin-left transform-gpu text-neutral-700 transition-all duration-300 ease-in-out group-hover:scale-75" /> */}
            <h3 className="text-[5rem] font-semibold text-neutral-700 dark:text-neutral-300">
              5.5
            </h3>
            <p className="max-w-lg text-neutral-500 text-[1.25rem]">pieces per Foot</p>
          </div>
        </div>

        <div
          className={cn(
            "group relative col-span-3 flex flex-col justify-between overflow-hidden rounded-xl",
            // light styles
            "bg-background [box-shadow:0_0_0_1px_rgba(0,0,0,.03),0_2px_4px_rgba(0,0,0,.05),0_12px_24px_rgba(0,0,0,.05)]",
            // dark styles
            "transform-gpu dark:bg-background dark:[border:1px_solid_rgba(255,255,255,.1)] dark:[box-shadow:0_-20px_80px_-20px_#ffffff1f_inset]",
            
            "lg:row-start-3 lg:row-end-4 lg:col-start-4 lg:col-end-6",
          )}
        >
          <div className="pointer-events-none z-10 flex flex-col gap-1 p-6 ">
            {/* <Icon className="h-12 w-12 origin-left transform-gpu text-neutral-700 transition-all duration-300 ease-in-out group-hover:scale-75" /> */}
            <h3 className="text-[4rem] font-semibold text-neutral-700 dark:text-neutral-300">
              Water Bottles
            </h3>
            <p className="max-w-lg text-neutral-500 text-[1.25rem]">are the most common pieces trash found</p>
          </div>
        </div>
      </BentoGrid>

    </div>
  )
}