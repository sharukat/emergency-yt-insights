import { useState, useCallback, useEffect } from "react";
import toast from "react-hot-toast";

export const useCollections = () => {
  const [collections, setCollections] = useState(() => {
    return [];
  });
  const [collection, setCollection] = useState<string>("");
  const [database, setDatabase] = useState(() => { return "" })

  const getCollections = async (db_name: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_URL}/collections?db_name=${db_name}`,
        {
          method: "GET",
          mode: "cors",
          headers: { "Content-Type": "application/json" },
        }
      );
      const data = await response.json();
      if (data.response) {
        setCollections(data.response);
        setDatabase(db_name)
      } else {
        toast.error("Received invalid response format from server");
      }
    } catch (error) {
      console.error("Submission error:", error);
      toast.error("Failed to get response from server");
    }
  };

  const handleCollections = useCallback((db_name: string) => {
    if (!collections || collections.length === 0 || database !== db_name) {
      getCollections(db_name);
    }
  }, [collections, database]);

  const handleCollectionSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCollection(e.target.value);
  };

  return { collections, getCollections, collection, handleCollections, handleCollectionSelect };
};
