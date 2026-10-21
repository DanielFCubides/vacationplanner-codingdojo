// USD amount as "$1,234.5", with the sign in front for negatives ("-$200").
const formatMoney = (amount: number): string =>
    `${amount < 0 ? "-" : ""}$${Math.abs(amount).toLocaleString()}`;

export {formatMoney};
