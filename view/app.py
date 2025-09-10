from __future__ import annotations

from typing import Any, Dict, Optional

import os
import sys
import asyncio
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from datetime import datetime
from zoneinfo import ZoneInfo

# Ensure project root is importable when running as a script
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from trade_buddy.broker import TradeBuddy


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = "change-me-in-prod"
    app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24  # 24 hours in seconds

    broker = TradeBuddy()

    def run_async(coro):
        return asyncio.run(coro)
    
    def _calculate_growth_percentage(acc, session):
        try:
            balance = getattr(acc, "balance", 0.0)
            base_balance = float(session.get("base_balance") or 0.0)
            if base_balance > 0:
                return ((balance - base_balance) / base_balance) * 100.0
            return 0.0
        except:
            return 0.0

    @app.before_request
    def _sync_broker_session():
        sid = session.get("session_id")
        if sid:
            try:
                # hydrate SDK session from Flask cookie on every request
                broker._current_session_id = sid
            except Exception:
                pass
        # Resolve current account once per request using JWT for speed
        g.account_obj = None
        jwt_token = session.get("jwt")
        if jwt_token:
            try:
                account = run_async(broker._get_auth_service().verify_token(jwt_token))
                g.account_obj = account
                # capture baseline balance at first login to compute growth
                if session.get("base_balance") is None:
                    session["base_balance"] = getattr(account, "balance", 0.0)
            except Exception:
                g.account_obj = None

    @app.context_processor
    def inject_globals():
        is_in = bool(session.get("session_id"))
        name = session.get("full_name")
        stats = None
        if is_in and getattr(g, "account_obj", None) is not None:
            acc = g.account_obj
            stats = {
                "balance": getattr(acc, "balance", 0.0),
                "total_margin": getattr(acc, "total_margin", 0.0),
                "utilized_margin": getattr(acc, "utilized_margin", 0.0),
                "available_margin": getattr(acc, "available_margin", 0.0),
                "margin_percentage": getattr(acc, "margin_percentage", 0.0),
            }
            base_balance = session.get("base_balance") or 0.0
            growth_pct = 0.0
            try:
                if base_balance and stats["balance"] is not None:
                    growth_pct = ((stats["balance"] - float(base_balance)) / float(base_balance)) * 100.0
            except Exception:
                growth_pct = 0.0
            stats["growth_percentage_since_login"] = growth_pct
        return {"is_logged_in": is_in, "account_name": name, "account_stats": stats}

    # Jinja filter to display datetimes in India timezone with AM/PM
    def india_time(value, fmt: str = "%d-%m-%Y %I:%M:%S %p IST") -> str:
        try:
            if value is None or value == "":
                return "-"
            dt: datetime
            if isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                except Exception:
                    return value
            elif isinstance(value, datetime):
                dt = value
            else:
                return str(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            ist = dt.astimezone(ZoneInfo("Asia/Kolkata"))
            return ist.strftime(fmt)
        except Exception:
            return str(value)

    app.jinja_env.filters["india_time"] = india_time

    @app.get("/")
    def home():
        if not session.get("session_id"):
            return redirect(url_for("login"))
        # Compose a lightweight summary for the hero section
        summary = {}
        if g.account_obj:
            acc = g.account_obj
            summary = {
                "full_name": getattr(acc, "full_name", ""),
                "email_id": getattr(acc, "email_id", ""),
                "balance": getattr(acc, "balance", 0.0),
                "available_margin": getattr(acc, "available_margin", 0.0),
                "utilized_margin": getattr(acc, "utilized_margin", 0.0),
                "margin_percentage": getattr(acc, "margin_percentage", 0.0),
                "default_leverage": getattr(acc, "default_leverage", 1.0),
                "growth_percentage": _calculate_growth_percentage(acc, session),
            }
        return render_template("home.html", summary=summary)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            user_id = request.form.get("user_id", "").strip()
            password = request.form.get("password", "").strip()
            if not user_id or not password:
                flash("Enter credentials", "error")
                return render_template("login.html")
            try:
                resp = run_async(broker.login({"user_id": user_id, "password": password}))
                if resp and resp.data:
                    session.permanent = True
                    session["session_id"] = resp.data.get("session_id")
                    session["jwt"] = resp.data.get("access_token")
                    account = resp.data.get("account") or {}
                    session["account_id"] = account.get("account_id")
                    session["full_name"] = account.get("full_name")
                    flash("Login successful", "success")
                    return redirect(url_for("home"))
                flash(resp.message if resp else "Login failed", "error")
            except Exception as e:
                flash(str(e), "error")
        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            form = request.form
            data: Dict[str, Any] = {
                "email_id": form.get("email", "").strip(),
                "password": form.get("password", "").strip(),
                "full_name": form.get("full_name", "").strip(),
                "max_trad_per_day": int(form.get("max_trad_per_day", 5)),
                "base_stoploss": float(form.get("base_stoploss", 5.0)),
                "base_target": float(form.get("base_target", 10.0)),
                "trailing_stoploss": float(form.get("trailing_stoploss", 10.0)),
                "trailing_target": float(form.get("trailing_target", 10.0)),
                "description": form.get("description", "Trade Buddy User").strip(),
            }
            try:
                resp = run_async(broker.registration(data))
                if resp and resp.data:
                    session["registration_result"] = resp.data
                    return redirect(url_for("register_success"))
                flash(resp.message if resp else "Registration failed", "error")
            except Exception as e:
                flash(str(e), "error")
        return render_template("register.html")

    @app.get("/register/success")
    def register_success():
        data = session.get("registration_result") or {}
        if not data:
            return redirect(url_for("register"))
        user = data.get("user") or {}
        token = data.get("verification_token")
        return render_template("register_success.html", user=user, token=token)

    @app.post("/verify-email")
    def verify_email():
        token = request.form.get("token", "").strip()
        if not token:
            flash("Token is required", "error")
            return redirect(request.referrer or url_for("register"))
        try:
            resp = run_async(broker.verify_email(token))
            if resp and resp.data:
                flash("Email verified successfully", "success")
            else:
                flash(resp.message if resp else "Verification failed", "error")
        except Exception as e:
            flash(str(e), "error")
        return redirect(url_for("login"))

    @app.get("/logout")
    def logout():
        try:
            if session.get("session_id"):
                run_async(broker.logout())
        finally:
            session.clear()
        flash("Logged out", "success")
        return redirect(url_for("login"))

    @app.get("/account")
    def account():
        if not session.get("session_id"):
            return redirect(url_for("login"))
        try:
            if g.account_obj is None:
                return redirect(url_for("login"))
            resp = run_async(broker.get_account_details(g.account_obj))
            data = (resp.data or {}).get("account") if resp else None
            # Ensure dict for template iteration
            if hasattr(data, "model_dump"):
                data = data.model_dump()
            return render_template("account.html", account=data)
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("home"))

    @app.route("/transactions", methods=["GET", "POST"])
    def transactions():
        if not session.get("session_id"):
            return redirect(url_for("login"))
        message = None
        if request.method == "POST":
            txn_type = request.form.get("transaction_type", "DEPOSIT")
            amount = float(request.form.get("amount", 0) or 0)
            note = request.form.get("note", "")
            try:
                if g.account_obj is None:
                    return redirect(url_for("login"))
                resp = run_async(broker.create_transaction(g.account_obj, {
                    "transaction_type": txn_type,
                    "amount": amount,
                    "note": note
                }))
                message = resp.message if resp else "Failed"
                flash(message, "success" if resp and resp.data else "error")
            except Exception as e:
                flash(str(e), "error")
        # fetch recent transactions to display (always after potential create)
        txns = []
        try:
            if g.account_obj:
                from trade_buddy.services.transaction_service import TransactionService
                ts = TransactionService()
                txns = run_async(ts.get_transaction_history(g.account_obj))
        except Exception:
            txns = []
        return render_template("transactions.html", transactions=txns)

    @app.route("/positions", methods=["GET", "POST"]) 
    def positions():
        if not session.get("session_id"):
            return redirect(url_for("login"))
        if request.method == "POST":
            form = request.form
            try:
                if g.account_obj is None:
                    return redirect(url_for("login"))
                symbol_id = form.get("symbol_id", "").strip()
                remaining_quantity = int(form.get("remaining_quantity", 1))
                price = float(form.get("price", 0))
                side = form.get("side", "BUY")
                stop = float(form.get("stoploss", 0) or 0)
                tgt = float(form.get("target", 0) or 0)
                resp = run_async(broker.open_position(
                    g.account_obj, symbol_id, remaining_quantity, price, side,
                    None if stop == 0 else stop,
                    None if tgt == 0 else tgt
                ))
                flash(resp.message if resp else "Failed", "success" if resp and resp.data else "error")
            except Exception as e:
                flash(str(e), "error")
        # fetch open positions to display
        positions = []
        closed_positions = []
        try:
            if g.account_obj:
                resp = run_async(broker.get_open_positions(g.account_obj))
                positions = (resp.data or {}).get("positions", []) if resp else []
                # also fetch closed position history for display
                hist_resp = run_async(broker.get_position_history(g.account_obj))
                closed_positions = (hist_resp.data or {}).get("positions", []) if hist_resp else []
        except Exception:
            positions = []
            closed_positions = []
        return render_template("positions.html", positions=positions, closed_positions=closed_positions)

    @app.post("/positions/action")
    def positions_action():
        if not session.get("session_id") or g.account_obj is None:
            return redirect(url_for("login"))
        action = request.form.get("action")
        pid = request.form.get("position_id")
        try:
            if action == "exit":
                exit_price = float(request.form.get("exit_price", 0) or 0)
                close_qty_raw = request.form.get("close_quantity")
                close_qty = float(close_qty_raw) if close_qty_raw else None
                resp = run_async(broker.exit_position(g.account_obj, pid, exit_price, close_qty))
                flash(resp.message if resp else "Failed", "success" if resp and resp.data else "error")
            elif action == "levels":
                sl = request.form.get("stoploss")
                tg = request.form.get("target")
                sl_val = float(sl) if sl else None
                tg_val = float(tg) if tg else None
                resp = run_async(broker.update_position_levels(g.account_obj, pid, sl_val, tg_val))
                flash(resp.message if resp else "Failed", "success" if resp and resp.data else "error")
            elif action == "pyramid":
                add_qty = float(request.form.get("additional_quantity", 0) or 0)
                new_price = float(request.form.get("new_price", 0) or 0)
                resp = run_async(broker.pyramid(g.account_obj, pid, add_qty, new_price))
                flash(resp.message if resp else "Failed", "success" if resp and resp.data else "error")
        except Exception as e:
            flash(str(e), "error")
        return redirect(url_for("positions"))


    @app.route("/settings", methods=["GET", "POST"]) 
    def settings():
        if not session.get("session_id") or g.account_obj is None:
            return redirect(url_for("login"))
        if request.method == "POST":
            try:
                lev = request.form.get("default_leverage")
                if lev:
                    resp = run_async(broker.update_leverage(g.account_obj, float(lev)))
                    flash(resp.message if resp else "Failed", "success" if resp and resp.data else "error")
                else:
                    flash("Enter leverage", "error")
                # refresh account in g
                token = session.get("jwt")
                if token:
                    g.account_obj = run_async(broker._get_auth_service().verify_token(token))
            except Exception as e:
                flash(str(e), "error")
        # current settings
        settings = {
            "default_leverage": getattr(g.account_obj, "default_leverage", 1.0),
        }
        return render_template("settings.html", settings=settings)

    @app.get("/notifications")
    def notifications():
        if not session.get("session_id") or g.account_obj is None:
            return redirect(url_for("login"))
        try:
            resp = run_async(broker.get_notifications(g.account_obj, 50))
            items = (resp.data or {}).get("notifications") if resp else []
            # Hide already read (status == 'SENT') from default list
            items = [n for n in items if getattr(n, 'status', None) != 'SENT']
        except Exception:
            items = []
        return render_template("notifications.html", notifications=items)

    @app.get("/notifications/all")
    def notifications_all():
        if not session.get("session_id") or g.account_obj is None:
            return redirect(url_for("login"))
        # pagination params
        try:
            page = int(request.args.get("page", 1))
        except Exception:
            page = 1
        try:
            resp = run_async(broker.get_notifications_paginated(g.account_obj, page, 20))
            items = (resp.data or {}).get("notifications") if resp else []
        except Exception:
            items = []
        next_page = page + 1
        prev_page = page - 1 if page > 1 else None
        return render_template("notifications_all.html", notifications=items, page=page, next_page=next_page, prev_page=prev_page)

    @app.post("/notifications/action")
    def notifications_action():
        if not session.get("session_id") or g.account_obj is None:
            return redirect(url_for("login"))
        nid = request.form.get("notification_id")
        try:
            resp = run_async(broker.read_notification(nid))
            flash(resp.message if resp else "Failed", "success" if resp and resp.data else "error")
        except Exception as e:
            flash(str(e), "error")
        return redirect(url_for("notifications"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)


