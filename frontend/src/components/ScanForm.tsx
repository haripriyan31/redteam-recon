"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Loader2 } from "lucide-react";

export function ScanForm() {
    const [domain, setDomain] = useState("");
    const [twitterHandle, setTwitterHandle] = useState("");
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    const handleScan = async () => {
        if (!domain) return;
        setLoading(true);

        try {
            const res = await fetch("http://localhost:8000/api/scan", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    domain,
                    twitter_handle: twitterHandle || null,
                    scan_types: ["all"]
                }),
            });

            if (!res.ok) {
                throw new Error("Failed to start scan");
            }

            const data = await res.json();
            console.log("Scan started:", data);
            router.push(`/scan/${data.id}`);

        } catch (error) {
            console.error(error);
            alert("Error starting scan. Make sure backend is running.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex w-full max-w-2xl flex-col items-center space-y-4 pt-6">
            <div className="flex w-full space-x-2">
                <Input
                    type="text"
                    placeholder="Target Domain (e.g. google.com)"
                    className="h-12 flex-1 text-lg shadow-sm"
                    value={domain}
                    onChange={(e) => setDomain(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleScan()}
                />
                <Input
                    type="text"
                    placeholder="Twitter Handle (Optional)"
                    className="h-12 w-1/3 text-lg shadow-sm"
                    value={twitterHandle}
                    onChange={(e) => setTwitterHandle(e.target.value)}
                />
                <Button
                    size="lg"
                    className="h-12 px-8 font-semibold shadow-md transition-all hover:scale-105"
                    onClick={handleScan}
                    disabled={loading}
                >
                    {loading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : <Search className="mr-2 h-5 w-5" />}
                    {loading ? "Scanning..." : "Start Scan"}
                </Button>
            </div>
        </div>
    );
}
