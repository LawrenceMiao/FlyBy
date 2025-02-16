import { cn } from "@/lib/utils";
import { useState } from "react";
import { BentoGrid } from "@/components/magicui/bento-grid";
import VideoPlayer from "@/components/VideoPlayer";


export default function Homepage() {
  const [data, setData] = useState({
    "Total tracked objects": 0,
    "Class counts:": { "N/A" : 0},
    "Frames processed": 0,
  });

  const findMostCommonObject = (data: any) => {
    const classCounts = data["Class counts:"];
    let mostCommonObject = null;
    let maxCount = 0;

    for (const [objectClass, count] of Object.entries(classCounts) as [string, number][]) {
      if (count !== undefined && count > maxCount) {
        maxCount = count;
        mostCommonObject = objectClass;
      }
    }

    return mostCommonObject;
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 pt-4">
      <h1 className="text-4xl text-[#0f4592] font-bold mb-4">FlyBy</h1>

      <BentoGrid className="p-8 pt-2">
        <div
          className={cn(
            "group relative col-span-3 flex flex-col justify-between overflow-hidden rounded-xl",
            // light styles
            "bg-background [box-shadow:0_0_0_1px_rgba(0,0,0,.03),0_2px_4px_rgba(0,0,0,.05),0_12px_24px_rgba(0,0,0,.05)]",
            // dark styles
            "transform-gpu dark:bg-background dark:[border:1px_solid_rgba(255,255,255,.1)] dark:[box-shadow:0_-20px_80px_-20px_#ffffff1f_inset]",
            
            "lg:row-start-1 lg:row-end-4 lg:col-start-1 lg:col-end-4",
            "md:row-start-1 md:row-end-4 md:col-start-1 md:col-end-6",
            "row-start-1 row-end-3 col-start-1 col-end-6"
          )}
        >
          <div className="w-full h-full pointer-events-none z-10 flex flex-col gap-1 p-6 ">
            <VideoPlayer />
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
            "md:row-start-4 md:row-end-6 md:col-start-1 md:col-end-4",
            "row-start-3 row-end-5 col-start-1 col-end-4 ",
          )}
        >
          <div className="pointer-events-none z-10 flex flex-col gap-1 p-6 ">
            <h3 className="text-[2rem] font-semibold text-[#0f4592] leading-tight mb-4">
              Trash Breakdown
            </h3>
            {data["Class counts:"] && Object.entries(data["Class counts:"]).map(([key, value]) => (
              <p className="max-w-lg text-neutral-500 text-[1.25rem]">
                <strong>{key}</strong> {value}
              </p>
            ))}
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
            "md:row-start-4 md:row-end-5 md:col-start-4 md:col-end-6",
            "row-start-4 row-end-5 col-start-4 col-end-6",
          )}
        >
          <div className="pointer-events-none z-10 flex flex-col gap-1 p-6 ">
            {/* <Icon className="h-12 w-12 origin-left transform-gpu text-neutral-700 transition-all duration-300 ease-in-out group-hover:scale-75" /> */}
            <h3 className="text-[4rem] md:text-[5rem] font-semibold text-[#0f4592]">
              {data["Total tracked objects"]}
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
            "md:row-start-5 md:row-end-6 md:col-start-4 md:col-end-6",
            "row-start-3 row-end-4 col-start-4 col-end-6",
          )}
        >
          <div className="pointer-events-none z-10 flex flex-col gap-1 p-6 ">
            {/* <Icon className="h-12 w-12 origin-left transform-gpu text-neutral-700 transition-all duration-300 ease-in-out group-hover:scale-75" /> */}
            <h3 className="text-[4rem] md:text-[5rem] font-semibold text-[#0f4592]">
              {data["Frames processed"]}
            </h3>
            <p className="max-w-lg text-neutral-500 text-[1.25rem]">total frames processed</p>
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
            "md:row-start-6 md:row-end-7 md:col-start-1 md:col-end-6",
            "row-start-5 row-end-6 col-start-1 col-end-6",
          )}
        >
          <div className="pointer-events-none z-10 flex flex-col gap-1 p-6 ">
            {/* <Icon className="h-12 w-12 origin-left transform-gpu text-neutral-700 transition-all duration-300 ease-in-out group-hover:scale-75" /> */}
            <h3 className="text-[4rem] font-semibold text-[#0f4592]">
              {findMostCommonObject(data)}
            </h3>
            <p className="max-w-lg text-neutral-500 text-[1.25rem]">are the most common pieces trash found</p>
          </div>
        </div>
      </BentoGrid>

    </div>
  )
}