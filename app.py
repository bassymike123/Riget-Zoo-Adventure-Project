import os
import base64
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_migrate import Migrate
import qrcode
import pyotp
import werkzeug.security import generate_password_hash, check_password_hash
from model import db, User

