# How to use the api?

As you know it, Sellaris was made to be a scalable, secure and maintanble e-commerce backend application, that is capable of powering any E-commerce online system / application. All you have to do, is to code the frontend application, to make calls to the backend system after you have hosted it.

This `doc` conveys enough will guide you through from installing the application, to using it's APIs

## Public Endpoints

## Staff protected endpoints

### BUlk Stock quantity update
req:
```json
{
    "updates":[
        {
            "variant_id":"3004a23f-2657-4e78-9148-d3ffaf0aff80",
            "quantity":30,
            "action":"INCREASE"
        },
        {
            "variant_id":"3004a23f-2657-4e78-9148-d3ffaf0aff80",
            "quantity":30,
            "action":"INCREASE"
        },
        {
            "variant_id":"3ab94213-8de0-489e-9a91-457fea4eec83",
            "quantity":30,
            "action":"INCREASE"
        }
    ]
}
```
res:
```json
{
    "detail": "Bulk stock quantity update successful"
}
```