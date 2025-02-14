import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import Data_retrieval

### ---------------- BENCHMARKING FUNCTIONS ---------------- ###
def compare_metrics(main_company_data, competitors_data):
    """Creates a DataFrame comparing key financial metrics across companies."""
    metrics = ["Revenue", "Net Profit", "Margins", "Total Assets", "Total Liabilities", "Equity", "Operating Cash Flow"]
    
    data = []
    
    # Main company data
    main_company_metrics = main_company_data.get("financial_metrics", {})
    data.append([main_company_data["name"]] + [main_company_metrics.get(metric, None) for metric in metrics])
    
    # Competitor data
    for competitor, details in competitors_data.items():
        competitor_metrics = details.get("financial_metrics", {})
        data.append([competitor] + [competitor_metrics.get(metric, None) for metric in metrics])
    
    # Create DataFrame
    df_comparison = pd.DataFrame(data, columns=["Company"] + metrics)
    return df_comparison


def plot_comparison(df_comparison):
    """Generates bar plots for key financial metrics."""
    df_comparison.set_index("Company", inplace=True)
    
    plt.figure(figsize=(12, 6))
    for metric in df_comparison.columns:
        plt.figure(figsize=(8, 5))
        sns.barplot(x=df_comparison.index, y=df_comparison[metric], palette="viridis")
        plt.title(f"Comparison of {metric}")
        plt.xticks(rotation=45)
        plt.ylabel(metric)
        plt.show()


def main():
    company_name = input("Enter the company name: ")
    competitors = input("Enter competitor names (comma-separated): ").split(",")
    competitors = [comp.strip() for comp in competitors]
    
    # Fetch data
    financial_data = Data_retrieval.fetch_data(company_name, competitors)
    
    # Extract main company and competitors data
    main_company_data = financial_data["main_company"]
    competitors_data = financial_data["competitors"]
    
    # Compare metrics
    df_comparison = compare_metrics(main_company_data, competitors_data)
    print("\nFinancial Metrics Comparison:")
    print(df_comparison)
    
    # Plot comparison
    plot_comparison(df_comparison)
    

if __name__ == "__main__":
    main()
