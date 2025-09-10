// ===== OSRS Safe Havens — Power Query (M) =====
// Creates a BasePath parameter so you can load CSVs from data/exports

let
    BasePath = #"[Set your local path]\osrs-safe-havens\data\exports",
    Items = Csv.Document(File.Contents(BasePath & "\items.csv"),[Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Prices = Csv.Document(File.Contents(BasePath & "\prices_daily.csv"),[Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Market = Csv.Document(File.Contents(BasePath & "\market_index_daily.csv"),[Delimiter=",", Columns=2, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Events = try Csv.Document(File.Contents(BasePath & "\game_events.csv"),[Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.Csv]) otherwise null,
    ItemReturns = try Csv.Document(File.Contents(BasePath & "\item_returns.csv"),[Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.Csv]) otherwise null,
    MktReturns = try Csv.Document(File.Contents(BasePath & "\mkt_returns.csv"),[Delimiter=",", Columns=2, Encoding=65001, QuoteStyle=QuoteStyle.Csv]) otherwise null,
    Drawdowns = try Csv.Document(File.Contents(BasePath & "\drawdowns.csv"),[Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.Csv]) otherwise null,

    // Promote headers & set types
    ItemsT = Table.PromoteHeaders(Items, [PromoteAllScalars=true]),
    ItemsTyped = Table.TransformColumnTypes(ItemsT,{{"item_id", Int64.Type},{"name", type text},{"category", type text},{"tradeable", Int64.Type},{"noted", Int64.Type}}),

    PricesT = Table.PromoteHeaders(Prices, [PromoteAllScalars=true]),
    PricesTyped = Table.TransformColumnTypes(PricesT,{{"item_id", Int64.Type},{"price_date", type date},{"avg_price_gp", type number},{"volume", type number}}),

    MarketT = Table.PromoteHeaders(Market, [PromoteAllScalars=true]),
    MarketTyped = Table.TransformColumnTypes(MarketT,{{"price_date", type date},{"mkt_index_gp", type number}}),

    EventsT = if Events <> null then Table.PromoteHeaders(Events, [PromoteAllScalars=true]) else null,
    EventsTyped = if EventsT <> null then Table.TransformColumnTypes(EventsT,{{"event_date", type date},{"label", type text},{"details", type text}}) else null,

    IR = if ItemReturns <> null then Table.PromoteHeaders(ItemReturns, [PromoteAllScalars=true]) else null,
    IRTyped = if IR <> null then Table.TransformColumnTypes(IR,{{"item_id", Int64.Type},{"price_date", type date},{"ret", type number}}) else null,

    MR = if MktReturns <> null then Table.PromoteHeaders(MktReturns, [PromoteAllScalars=true]) else null,
    MRTyped = if MR <> null then Table.TransformColumnTypes(MR,{{"price_date", type date},{"mkt_ret", type number}}) else null,

    DD = if Drawdowns <> null then Table.PromoteHeaders(Drawdowns, [PromoteAllScalars=true]) else null,
    DDTyped = if DD <> null then Table.TransformColumnTypes(DD,{{"item_id", Int64.Type},{"price_date", type date},{"drawdown", type number}}) else null
in
    [
        items = ItemsTyped,
        prices_daily = PricesTyped,
        market_index_daily = MarketTyped,
        game_events = EventsTyped,
        item_returns = IRTyped,
        mkt_returns = MRTyped,
        drawdowns = DDTyped
    ]
