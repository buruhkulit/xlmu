from dotenv import load_dotenv

from app.service.git import check_for_updates
load_dotenv()

import sys, json
from datetime import datetime
from app.menus.util import clear_screen, pause
from app.client.engsel import (
    get_balance,
    get_tiering_info,
)
from app.client.famplan import validate_msisdn
from app.menus.payment import show_transaction_history
from app.service.auth import AuthInstance
from app.menus.account import show_account_menu
from app.menus.package import fetch_my_packages, get_packages_by_family, show_package_details
from app.menus.paket import show_paket_menu1
from app.service.sentry import enter_sentry_mode
from app.menus.purchase import purchase_by_family
from app.menus.notification import show_notification_menu

WIDTH = 55
def show_main_menu(profile):
    clear_screen()
    # Warna ANSI sederhana
    BOLD = "\033[1m"
    RESET = "\033[0m"
    
    expired_at_dt = datetime.fromtimestamp(profile["balance_expired_at"]).strftime("%Y-%m-%d")
    
    # --- HEADER DASHBOARD ---
    print(f"{BOLD}{' DASHBOARD AKUN '.center(WIDTH)}{RESET}")
    print(f" ".center(WIDTH))
    
    # Mengelompokkan menu agar lebih rapi
    header = [
        f" {BOLD}Nomor  :{RESET} {profile['number']} ({profile['subscription_type']})",
        f" {BOLD}Pulsa  :{RESET} Rp {profile['balance']:,}",
        f" {BOLD}Aktif  :{RESET} {expired_at_dt}",
        f" {BOLD}Points :{RESET} {profile['point_info']}",
    ]
    for menu in header:
        print(f"  {menu}")
        
    # --- MENU CATEGORIES ---
    print(f" ".center(WIDTH))
    print(f"\n{BOLD}{' MAIN MENU '.center(WIDTH)}{RESET}")
    print(f" ".center(WIDTH))

    # Mengelompokkan menu agar lebih rapi
    menus = [
        f"{BOLD}1.{RESET} Login/Ganti Akun",
        f"{BOLD}2.{RESET} Paket Saya",
        f"{BOLD}3.{RESET} Beli Paket 1",
        f"{BOLD}4.{RESET} Family Code"
    ]
    for menu in menus:
        print(f"  {menu}")
        
    print(f" ".center(WIDTH))
    print(f"\n{BOLD}{' TOOLS & SYSTEM '.center(WIDTH)}{RESET}")
    print(f" ".center(WIDTH))

    # Mengelompokkan menu agar lebih rapi
    tools = [
        f" {BOLD}N.{RESET} Notifikasi",
        f" {BOLD}99.{RESET} Tutup App"),
    ]
    for menu in tools:
        print(f"  {menu}")
    print(f" ".center(WIDTH))       

show_menu = True
def main():
    
    while True:
        active_user = AuthInstance.get_active_user()

        # Logged in
        if active_user is not None:
            balance = get_balance(AuthInstance.api_key, active_user["tokens"]["id_token"])
            balance_remaining = balance.get("remaining")
            balance_expired_at = balance.get("expired_at")
            
            point_info = "Points: N/A | Tier: N/A"
            
            if active_user["subscription_type"] == "PREPAID":
                tiering_data = get_tiering_info(AuthInstance.api_key, active_user["tokens"])
                tier = tiering_data.get("tier", 0)
                current_point = tiering_data.get("current_point", 0)
                point_info = f"{current_point} (Tier {tier})"
                
            
            profile = {
                "number": active_user["number"],
                "subscriber_id": active_user["subscriber_id"],
                "subscription_type": active_user["subscription_type"],
                "balance": balance_remaining,
                "balance_expired_at": balance_expired_at,
                "point_info": point_info
            }

            show_main_menu(profile)

            choice = input("Pilih menu: ")
            # Testing shortcuts
            if choice.lower() == "t":
                pause()
            elif choice == "1":
                selected_user_number = show_account_menu()
                if selected_user_number:
                    AuthInstance.set_active_user(selected_user_number)
                else:
                    print("No user selected or failed to load user.")
                continue
            elif choice == "2":
                fetch_my_packages()
                continue
            elif choice == "3":
                show_paket_menu1()
            elif choice == "4":
                family_code = input("Enter family code (or '99' to cancel): ")
                if family_code == "99":
                    continue
                get_packages_by_family(family_code)
            elif choice == "00":
                show_bookmark_menu()
            elif choice == "99":
                print("Exiting the application.")
                sys.exit(0)
            elif choice.lower() == "n":
                show_notification_menu()
if __name__ == "__main__":
    try:
        print("Checking for updates...")
        need_update = check_for_updates()
        if need_update:
            pause()

        main()
    except KeyboardInterrupt:
        print("\nExiting the application.")
    # except Exception as e:
    #     print(f"An error occurred: {e}")
