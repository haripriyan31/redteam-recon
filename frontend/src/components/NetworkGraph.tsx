"use client";

import dynamic from 'next/dynamic';
import { useMemo } from 'react';

// Dynamically import force-graph to avoid SSR issues
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false });

interface NetworkGraphProps {
    data: any;
}

export default function NetworkGraph({ data }: NetworkGraphProps) {
    const graphData = useMemo(() => {
        if (!data) return { nodes: [], links: [] };

        const nodes: any[] = [];
        const links: any[] = [];
        const addedNodes = new Set();

        // Helper to add unique nodes
        const addNode = (id: string, group: number, val: number, label: string) => {
            if (!addedNodes.has(id)) {
                nodes.push({ id, group, val, name: label || id });
                addedNodes.add(id);
            }
        };

        // 1. Root Domain (Red)
        const rootId = data.domain;
        addNode(rootId, 1, 20, data.domain);

        // 2. Subdomains (Blue)
        data.subdomains?.subdomains?.forEach((sub: string) => {
            addNode(sub, 2, 10, sub);
            links.push({ source: rootId, target: sub });

            // Connect subdomain to IPs if available (mock logic or real if structured)
            // For now, let's link subdomains to the main IP if they resolve there, 
            // but we only have IP for main domain in Ports usually.
        });

        // 3. IPs and Ports (Green / Orange)
        data.ports?.forEach((p: any) => {
            const ip = p.ip;
            addNode(ip, 3, 15, ip);
            links.push({ source: rootId, target: ip }); // Assuming main domain resolves here

            p.ports.forEach((portInfo: any) => {
                const port = typeof portInfo === 'object' ? portInfo.port : portInfo;
                const portId = `${ip}:${port}`;
                const portLabel = typeof portInfo === 'object' ? `${port} (${portInfo.service})` : `${port}`;

                addNode(portId, 4, 5, portLabel);
                links.push({ source: ip, target: portId });
            });
        });

        // 4. Vulnerabilities (Red Alert)
        data.vulnerabilities?.forEach((vuln: string, i: number) => {
            const vulnId = `vuln_${i}`;
            addNode(vulnId, 5, 8, "VULN");
            links.push({ source: rootId, target: vulnId });
        });

        return { nodes, links };
    }, [data]);

    return (
        <div className="border rounded-lg overflow-hidden bg-slate-950 h-[500px]">
            <ForceGraph2D
                graphData={graphData}
                nodeAutoColorBy="group"
                nodeLabel="name"
                width={800}
                height={500}
                backgroundColor="#020617"
                linkColor={() => "#ffffff30"}
                nodeCanvasObject={(node: any, ctx, globalScale) => {
                    const label = node.name;
                    const fontSize = 12 / globalScale;
                    ctx.font = `${fontSize}px Sans-Serif`;
                    const textWidth = ctx.measureText(label).width;
                    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

                    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
                    if (node.group === 1) ctx.fillStyle = '#ef4444'; // Red for Domain
                    if (node.group === 2) ctx.fillStyle = '#3b82f6'; // Blue for Sub
                    if (node.group === 3) ctx.fillStyle = '#22c55e'; // Green for IP
                    if (node.group === 4) ctx.fillStyle = '#f97316'; // Orange for Port
                    if (node.group === 5) ctx.fillStyle = '#b91c1c'; // Dark Red for Vuln

                    ctx.beginPath();
                    ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
                    ctx.fill();

                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = 'white';
                    ctx.fillText(label, node.x, node.y + 8);
                }}
            />
        </div>
    );
}
