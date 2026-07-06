import { FoodGridSkeleton, SectionHeading } from "@/components/states";

/** Route-level loading UI shown while the menu data streams in. */
export default function MenuLoading() {
  return (
    <main className="container-page py-14">
      <SectionHeading
        eyebrow="The Menu"
        title="Every dish, one place"
        description="Filter by category or search for your favourite dish."
      />
      <div className="skeleton mt-8 h-12 w-full max-w-md rounded-full" />
      <div className="mt-10">
        <FoodGridSkeleton count={6} />
      </div>
    </main>
  );
}
