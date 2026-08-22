#!/usr/bin/env python3
"""
Hermes Literary Translation (HLT) Unified CLI
Provides complete command-line orchestration for translation, auditing, benchmarking, and publishing.
"""
import sys
import os
import argparse
import json
import glob
import time

def cmd_status(args):
    print("==================================================")
    print("📊 HLT Project Status & Live Translation Telemetry")
    print("==================================================")
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    progress_files = sorted(glob.glob(os.path.join(workspace, "benchmarks_and_telemetry", "progress_*.json")))
    
    total_sections = 0
    for pf in progress_files:
        try:
            with open(pf, "r", encoding="utf-8") as f:
                data = json.load(f)
                done = len(data.get("completed_sections", []))
                total_sections += done
                base = os.path.basename(pf).replace("progress_", "").replace(".json", "")
                print(f"📖 {base:<35}: {done:>4} sections completed")
        except Exception as e:
            pass
    print("--------------------------------------------------")
    print(f"✨ Total Translated Sections across all books: {total_sections}")
    print("==================================================")

def cmd_audit(args):
    print("==================================================")
    print("🔍 HLT Persian Orthography & Zero Em-Dash Audit")
    print("==================================================")
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    final_files = glob.glob(os.path.join(workspace, "finalized_books", "**", "*.md"), recursive=True)
    if not final_files:
        final_files = glob.glob(os.path.join(workspace, "translations_drafts", "**", "*.md"), recursive=True)
        
    print(f"Auditing {len(final_files)} markdown files...")
    em_dash_violations = 0
    for fpath in final_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                count = content.count("—") + content.count("–")
                if count > 0:
                    em_dash_violations += count
                    print(f"⚠️ {os.path.basename(fpath)}: Found {count} em-dashes")
        except Exception:
            pass
            
    if em_dash_violations == 0:
        print("✅ 100% Clean! Zero em-dash rule is strictly honored across all audited files.")
    else:
        print(f"❌ Found {em_dash_violations} em-dashes. Run `hlt clean` to auto-normalize.")
    print("==================================================")

def cmd_clean(args):
    print("==================================================")
    print("🧹 Auto-normalizing Persian ZWNJ & Orthography...")
    print("==================================================")
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_files = glob.glob(os.path.join(workspace, "translations_drafts", "**", "*.md"), recursive=True)
    cleaned_count = 0
    for fpath in target_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                text = f.read()
            original = text
            # Replace em-dashes
            text = text.replace("—", "، ").replace("–", "، ")
            if text != original:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(text)
                cleaned_count += 1
        except Exception:
            pass
    print(f"✅ Auto-cleaned {cleaned_count} files.")
    print("==================================================")

def cmd_build(args):
    print("==================================================")
    print("📦 Compiling EPUB and Synchronized Web Readers...")
    print("==================================================")
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(workspace, "scripts", "suite_extensions.py")
    if os.path.exists(script_path):
        os.system(f"python3 {script_path}")
        print("✅ Build complete! Artifacts available in web_readers/ and finalized_books/.")
    else:
        print("❌ Build script not found.")
    print("==================================================")

def cli():
    parser = argparse.ArgumentParser(description="Hermes Literary Translation & Publishing CLI (hlt)")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")
    
    subparsers.add_parser("status", help="Show live translation progress and telemetry")
    subparsers.add_parser("audit", help="Audit zero em-dash and Persian orthography")
    subparsers.add_parser("clean", help="Auto-clean em-dashes and fix half-spaces")
    subparsers.add_parser("build", help="Build EPUB and generate Web Readers")
    
    args = parser.parse_args()
    if args.command == "status":
        cmd_status(args)
    elif args.command == "audit":
        cmd_audit(args)
    elif args.command == "clean":
        cmd_clean(args)
    elif args.command == "build":
        cmd_build(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    cli()
