from scraper.gasolinerar_xls import generate_geosjon_from_xls

def main():
    try:
        generate_geosjon_from_xls()
    except Exception as e:
        print(f"Error in main: {e}")
        raise e
    finally:
        print("Execution completed.")
        
if __name__ == "__main__":
    main()