# Mortgage-Calcululator

This project is aimed at designing and developing an interactive dashboard that helps analyze & visualize details of a mortgage specified by a user. It allows for a quick calculation of installments, generating payment schedule and estimating total cost of a mortgage. The _Mortgage Calculator_ helps comparing various mortgage options (fixed or descending installment, installment and cost variability based on interest rates).

The tool works best for analyzing a mortgage offered by Polish banks, where the total interest usually consists of WIBOR interest rate and bank interest rate. However, it can also be used for any other type of mortgage - if there is no WIBOR/central bank interest rate, just set it as 0.

## Demo

You can test the application on your own, as it was already deployed - please visit: https://mortgage-calculator-vvbs.onrender.com/

## Authors

- [@SoltJak](https://github.com/SoltJak)

## Tech Stack

**UI:** Python-Dash

**UI styling:** Bootstrap

**Data handling:** Python-Pandas

## Screenshots
### Main application screen - high level information on specified mortgage
![Main_screen](https://user-images.githubusercontent.com/64710053/217364663-bcb6deef-a1f8-405b-b431-779709d87cbb.png)


### Mortgage payment simulation chart - one of available visualizations
![Payment simulation screen](https://user-images.githubusercontent.com/64710053/217364831-328d91c4-e0d5-4b27-84e5-a66b77fea5cb.png)

## Roadmap

Although the main part of the tool is already developed and deployed, there are potential enhancement ideas identified:
- include additional visualizations for even better understanding of mortgage cost and its details
- add an option to calculate impact of mortgage overpayment - pay your mortgage earlier of decrease your installment

## Feedback

If you have any feedback, please reach out to me at jakub.soltysiuk@gmail.com
