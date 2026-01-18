import Link from "next/link";
import { Shield, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Navbar() {
    return (
        <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-14 max-w-screen-2xl items-center mx-auto px-4">
                <Link href="/" className="mr-6 flex items-center space-x-2">
                    <Shield className="h-6 w-6 text-primary" />
                    <span className="hidden font-bold sm:inline-block">
                        ReconToolkit
                    </span>
                </Link>
                <div className="mr-4 hidden md:flex">
                    <nav className="flex items-center space-x-6 text-sm font-medium">
                        <Link
                            href="/"
                            className="transition-colors hover:text-foreground/80 text-foreground"
                        >
                            Dashboard
                        </Link>
                        <Link
                            href="/scans"
                            className="transition-colors hover:text-foreground/80 text-foreground/60"
                        >
                            History
                        </Link>
                        <Link href="https://github.com" className="transition-colors hover:text-foreground/80 text-foreground/60">
                            Documentation
                        </Link>
                    </nav>
                </div>
                <div className="flex flex-1 items-center justify-end space-x-2">
                    <Link href="/">
                        <Button variant="default" size="sm">
                            <Plus className="mr-2 h-4 w-4" />
                            New Scan
                        </Button>
                    </Link>
                </div>
            </div>
        </nav>
    );
}
