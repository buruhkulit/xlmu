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
from app.menus.bookmark import show_bookmark_menu
from app.menus.account import show_account_menu
from app.menus.package import fetch_my_packages, get_packages_by_family, show_package_details
from app.menus.paket import show_paket_menu1, show_paket_menu2
from app.service.sentry import enter_sentry_mode
from app.menus.purchase import purchase_by_family
from app.menus.famplan import show_family_info
from app.menus.circle import show_circle_info
from app.menus.notification import show_notification_menu
from app.menus.store.segments import show_store_segments_menu
from app.menus.store.search import show_family_list_menu, show_store_packages_menu
from app.menus.store.redemables import show_redeemables_menu
from app.client.registration import dukcapil

from datetime import datetime

def show_main_menu(profile):
    clear_screen()
    BOLD, RESET = "\033[1m", "\033[0m"
    WIDTH = 55

    # Helper untuk cetak header bagian
    def print_section(title):
        print(f"\n{BOLD}{title.center(WIDTH)}{RESET}")
        print(" " * WIDTH) # Memberikan spasi kosong di bawah judul

    # Helper untuk cetak menu dalam kolom
    def print_grid(items, padding=31):
        for left, right in items:
            print(f"  {left.ljust(padding)} {right}")

    # 1. Dashboard Info
    expired = datetime.fromtimestamp(profile["balance_expired_at"]).strftime("%Y-%m-%d")
    print_section("DASHBOARD AKUN")
    print_grid([
        (f" {BOLD}Nomor  :{RESET} {profile['number']} ({profile['subscription_type']})", ""),
        (f" {BOLD}Pulsa  :{RESET} Rp {profile['balance']:,}", ""),
        (f" {BOLD}Aktif  :{RESET} {expired}", ""),
        (f" {BOLD}Points :{RESET} {profile['point_info']}", ""),
    ], padding=27)

    # 2. Main Menu
    print_section("MAIN MENU")
    print_grid([
        (f" {BOLD}1.{RESET} Login/Ganti Akun", f" {BOLD}8.{RESET} Riwayat Tx"),
        (f" {BOLD}2.{RESET} Paket Saya",        f" {BOLD}9.{RESET} Family Plan"),
        (f" {BOLD}3.{RESET} Beli Paket 1",      f"{BOLD}10.{RESET} Circle"),
        (f" {BOLD}4.{RESET} Beli Paket 2",      f"{BOLD}11.{RESET} Store Segments"),
        (f" {BOLD}5.{RESET} Option Code",       f"{BOLD}12.{RESET} Family List"),
        (f" {BOLD}6.{RESET} Family Code",       f"{BOLD}13.{RESET} Store Packages"),
        (f" {BOLD}7.{RESET} Bulk Buy (Loop)",   f"{BOLD}14.{RESET} Redeemables"),
    ])

    # 3. Tools & System
    print_section("TOOLS & SYSTEM")
    print_grid([
        (f" {BOLD}N.{RESET} Notifikasi",      f" {BOLD}00.{RESET} Bookmark"),
        (f" {BOLD}R.{RESET} Register",        f" {BOLD}99.{RESET} Tutup App"),
        (f" {BOLD}V.{RESET} Validate MSISDN", ""),
    ])
    print("\n" + " " * WIDTH)

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
