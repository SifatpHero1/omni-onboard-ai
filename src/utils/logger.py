import logging
import sys
from pathlib import Path

def setup_logger(name: str = "omni_onboard") -> logging.Logger:
    """লগার সেটআপ করা"""
    
    # logs ফোল্ডার তৈরি করা (যদি না থাকে)
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # যদি আগে থেকে হ্যান্ডলার থাকে, ডুপ্লিকেট এড়াতে ক্লিয়ার করে দেওয়া
    if logger.hasHandlers():
        logger.handlers.clear()

    # কনসোলে দেখানোর জন্য ফরম্যাট
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # ফাইলে সেভ করার জন্য ফরম্যাট
    file_handler = logging.FileHandler(log_dir / "workflow.log", encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_format)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# গ্লোবাল লগার ইনস্ট্যান্স
logger = setup_logger()