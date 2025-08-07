"""
Configuration file for Discord Member Bot.
Modify these settings as needed for your server.
"""

import os

BOT_CONFIG = {
    # The name of the role to assign to new members
    'MEMBER_ROLE_NAME': os.getenv('MEMBER_ROLE_NAME', 'member'),
    
    # Whether to send a welcome message to new members via DM
    'SEND_WELCOME_MESSAGE': os.getenv('SEND_WELCOME_MESSAGE', 'false').lower() == 'true',
    
    # Welcome message template (if enabled)
    # Available placeholders: {member}, {guild}, {role}
    'WELCOME_MESSAGE': os.getenv('WELCOME_MESSAGE', 
        'Welcome to {guild}, {member}! You have been automatically assigned the "{role}" role.'),
    
    # Bot settings
    'COMMAND_PREFIX': os.getenv('COMMAND_PREFIX', '!'),
    
    # Logging settings
    'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
}

# Validate configuration
if not BOT_CONFIG['MEMBER_ROLE_NAME']:
    raise ValueError('MEMBER_ROLE_NAME cannot be empty')

# Convert log level string to logging constant
import logging
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

BOT_CONFIG['LOG_LEVEL'] = LOG_LEVELS.get(BOT_CONFIG['LOG_LEVEL'].upper(), logging.INFO)
