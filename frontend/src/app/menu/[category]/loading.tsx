import { FoodGridSkeleton } from "@/components/states";

/** Loading UI for category and item detail routes. */
export default function CategoryLoading() {
  return (
    <main className="container-page py-14">
      <div className="mb-6 h-4 w-40 skeleton rounded" />
      <div className="h-10 w-64 skeleton rounded" />
      <div className="mt-10">
        <FoodGridSkeleton count={6} />
      </div>
    </main>
  );
}
