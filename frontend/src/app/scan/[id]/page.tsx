"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2, CheckCircle2, AlertCircle, Globe, Server, Cpu, ExternalLink, Calendar, Camera, ShieldAlert, AlertTriangle } from "lucide-react";

interface SubdomainResult {
    subdomains: string[];
    count: number;
}

interface PortResult {
    ip: string;
    ports: number[];
}

interface OSINTArtifact {
    value: string;
    type: string;
    source: string;
    confidence: number;
}

interface ScanResult {
    id: string;
    domain: string;
    status: "pending" | "running" | "completed" | "failed";
    timestamp: string;
    subdomains: SubdomainResult | null;
    ports: PortResult[] | null;
    technologies: string[] | null;
    osint_data?: OSINTArtifact[];
    directories?: string[];
    screenshots?: Record<string, string>;
    vulnerabilities?: string[];
    attack_score?: number;
}

export default function ScanResultsPage() {

    const params = useParams();
    const [results, setResults] = useState<ScanResult | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchResults = async () => {
        try {
            const res = await fetch(`http://localhost:8000/api/scan/${params.id}`);
            if (res.ok) {
                const data = await res.json();
                setResults(data);
                if (data.status === "completed" || data.status === "failed") {
                    setLoading(false);
                }
            }
        } catch (error) {
            console.error(error);
        }
    };

    useEffect(() => {
        fetchResults();
        // Poll every 2 seconds if running
        const interval = setInterval(() => {
            if (results?.status !== "completed" && results?.status !== "failed") {
                fetchResults();
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [results?.status]);

    if (!results && loading) return (
        <div className="flex flex-col items-center justify-center h-[50vh]">
            <Loader2 className="w-12 h-12 animate-spin text-primary mb-4" />
            <h2 className="text-xl font-semibold">Initializing Scan...</h2>
        </div>
    );

    return (
        <div className="space-y-8 py-8 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">{results?.domain}</h1>
                    <div className="flex items-center mt-2 space-x-2 text-muted-foreground">
                        <Calendar className="w-4 h-4" />
                        <span className="text-sm">Scanned on {new Date(results?.timestamp || "").toLocaleString()}</span>
                        {results?.status === 'running' && <span className="text-blue-400 animate-pulse text-sm ml-2 font-medium">• Scanning in Progress...</span>}
                    </div>
                </div>
                <div className="text-right flex space-x-2">
                    <Button variant="outline" onClick={() => window.open(`http://localhost:8000/api/scan/${results?.id}/export/spiderfoot`, '_blank')}>
                        Export SpiderFoot
                    </Button>
                    <Button variant="outline" onClick={() => window.location.reload()}>Refresh Results</Button>
                </div>
            </div>

            {/* Summary Grid */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Subdomains</CardTitle>
                        <Globe className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{results?.subdomains?.count || 0}</div>
                        <p className="text-xs text-muted-foreground">Discovered assets</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Open Ports</CardTitle>
                        <Server className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{results?.ports?.[0]?.ports.length || 0}</div>
                        <p className="text-xs text-muted-foreground">Active services</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">OSINT Artifacts</CardTitle>
                        <AlertCircle className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{results?.osint_data?.length || 0}</div>
                        <p className="text-xs text-muted-foreground">Emails, Phones, Docs</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Technologies</CardTitle>
                        <Cpu className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{results?.technologies?.length || 0}</div>
                        <p className="text-xs text-muted-foreground">Stack detected</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Visuals</CardTitle>
                        <Camera className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{Object.keys(results?.screenshots || {}).length}</div>
                        <p className="text-xs text-muted-foreground">Screenshots captured</p>
                    </CardContent>
                </Card>
                <Card className={results?.attack_score && results.attack_score > 50 ? "border-red-500 bg-red-500/10" : ""}>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Attack Score</CardTitle>
                        <ShieldAlert className={results?.attack_score && results.attack_score > 50 ? "h-4 w-4 text-red-500" : "h-4 w-4 text-muted-foreground"} />
                    </CardHeader>
                    <CardContent>
                        <div className={`text-2xl font-bold ${results?.attack_score && results.attack_score > 50 ? "text-red-500" : ""}`}>{results?.attack_score || 0}</div>
                        <p className="text-xs text-muted-foreground">Risk Level: {results?.attack_score && results.attack_score > 50 ? "High" : "Low"}</p>
                    </CardContent>
                </Card>
            </div>

            {/* OSINT Results Section */}
            {results?.osint_data && results.osint_data.length > 0 && (
                <Card className="border-blue-900/50 bg-blue-950/10">
                    <CardHeader>
                        <CardTitle className="text-blue-400 flex items-center">
                            <Globe className="w-5 h-5 mr-2" />
                            OSINT Discovery Results
                        </CardTitle>
                        <CardDescription>
                            Publicly available information scraped from various sources.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {/* Emails */}
                            <div className="space-y-2">
                                <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Emails</h3>
                                <div className="space-y-1">
                                    {results.osint_data.filter(i => i.type === 'email').map((item, i) => (
                                        <div key={i} className="flex items-center justify-between text-sm p-2 rounded bg-muted/50 border">
                                            <span className="font-mono truncate" title={item.value}>{item.value}</span>
                                            <Badge variant="secondary" className="text-[10px] h-5">{item.source}</Badge>
                                        </div>
                                    ))}
                                    {results.osint_data.filter(i => i.type === 'email').length === 0 && <span className="text-sm text-muted-foreground">None found</span>}
                                </div>
                            </div>
                            {/* Phones */}
                            <div className="space-y-2">
                                <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Phone Numbers</h3>
                                <div className="space-y-1">
                                    {results.osint_data.filter(i => i.type === 'phone').map((item, i) => (
                                        <div key={i} className="flex items-center justify-between text-sm p-2 rounded bg-muted/50 border">
                                            <span className="font-mono">{item.value}</span>
                                            <Badge variant="secondary" className="text-[10px] h-5">{item.source}</Badge>
                                        </div>
                                    ))}
                                    {results.osint_data.filter(i => i.type === 'phone').length === 0 && <span className="text-sm text-muted-foreground">None found</span>}
                                </div>
                            </div>
                            {/* Docs/PDFs */}
                            <div className="space-y-2">
                                <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Documents (PDFs)</h3>
                                <div className="space-y-1">
                                    {results.osint_data.filter(i => i.type === 'pdf').map((item, i) => (
                                        <div key={i} className="flex items-center justify-between text-sm p-2 rounded bg-muted/50 border">
                                            <a href={item.value} target="_blank" className="font-mono text-blue-400 hover:underline truncate max-w-[200px]" title={item.value}>
                                                {item.value.split('/').pop()}
                                            </a>
                                            <Badge variant="secondary" className="text-[10px] h-5">PDF</Badge>
                                        </div>
                                    ))}
                                    {results.osint_data.filter(i => i.type === 'pdf').length === 0 && <span className="text-sm text-muted-foreground">None found</span>}
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            <div className="grid gap-6 md:grid-cols-2">
                {/* Open Ports */}
                <Card className="col-span-1">
                    <CardHeader>
                        <CardTitle>Open Ports & Services</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {results?.ports && results.ports.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                                {results.ports[0].ports.map((port: number) => (
                                    <Badge key={port} variant="secondary" className="px-3 py-1 text-sm bg-green-950 text-green-400 hover:bg-green-900 border-green-900">
                                        Port {port}
                                    </Badge>
                                ))}
                            </div>
                        ) : (
                            <p className="text-muted-foreground text-sm">No open ports found or scan failed.</p>
                        )}
                    </CardContent>
                </Card>

                {/* Technologies */}
                <Card className="col-span-1">
                    <CardHeader>
                        <CardTitle>Technology Stack</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {results?.technologies && results.technologies.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                                {results.technologies.map((tech: string, i: number) => (
                                    <Badge key={i} variant="outline" className="px-3 py-1 text-sm">
                                        {tech}
                                    </Badge>
                                ))}
                            </div>
                        ) : (
                            <p className="text-muted-foreground text-sm">No technologies detected.</p>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Visual Recon Gallery */}
            {results?.screenshots && Object.keys(results.screenshots).length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Visual Reconnaissance</CardTitle>
                        <CardDescription>Screenshots of discovered subdomains.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {Object.entries(results.screenshots).map(([domain, b64]: [string, any]) => (
                                <div key={domain} className="group relative border rounded-lg overflow-hidden bg-background">
                                    <div className="aspect-video w-full bg-muted relative">
                                        <img
                                            src={b64}
                                            alt={`Screenshot of ${domain}`}
                                            className="object-cover w-full h-full transition-transform group-hover:scale-105"
                                        />
                                    </div>
                                    <div className="p-3 border-t">
                                        <h3 className="font-semibold text-sm truncate">{domain}</h3>
                                        <a href={`http://${domain}`} target="_blank" className="text-xs text-blue-500 hover:underline flex items-center mt-1">
                                            Visit Site <ExternalLink className="w-3 h-3 ml-1" />
                                        </a>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Directory Fuzzing Results */}
            {results?.directories && results.directories.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Directory & File Discovery</CardTitle>
                        <CardDescription>Interesting paths found via dictionary attack.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                            {results.directories.map((dir: string, i: number) => (
                                <li key={i} className="flex items-center p-2 rounded bg-muted/50">
                                    <AlertTriangle className="w-4 h-4 text-yellow-500 mr-2" />
                                    <span className="font-mono">{dir}</span>
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            )}

            {/* Vulnerability Report */}
            {results?.vulnerabilities && results.vulnerabilities.length > 0 && (
                <Card className="border-red-900/50 bg-red-950/10">
                    <CardHeader>
                        <CardTitle className="text-red-500 flex items-center">
                            <ShieldAlert className="w-5 h-5 mr-2" />
                            Potential Vulnerabilities
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {results.vulnerabilities.map((vuln: string, i: number) => (
                                <div key={i} className="flex items-start p-3 bg-red-950/20 rounded-md border border-red-900/30">
                                    <AlertTriangle className="w-5 h-5 text-red-500 mr-3 mt-0.5" />
                                    <div>
                                        <p className="font-medium text-red-100">{vuln}</p>
                                        <p className="text-sm text-red-300/80 mt-1">
                                            Check version against NVD or run targeted exploit check.
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Subdomain List */}
            <Card>
                <CardHeader>
                    <CardTitle>Subdomains List</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="max-h-[300px] overflow-y-auto space-y-1">
                        {results?.subdomains?.subdomains.map((sub: string, i: number) => (
                            <div key={i} className="p-2 hover:bg-muted/50 rounded flex justify-between group">
                                <span className="text-sm font-mono">{sub}</span>
                                <a href={`http://${sub}`} target="_blank" className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-foreground">
                                    <ExternalLink className="w-4 h-4" />
                                </a>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
