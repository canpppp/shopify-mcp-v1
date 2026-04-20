--- shopify-mcp-v1/server.py	2026-04-19 23:49:01.000000000 +0000
+++ shopify-mcp-v1-new/server.py	2026-04-20 00:00:00.342078222 +0000
@@ -731,6 +731,246 @@
         return _error(e)
 
 
+class GetCollectionInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    collection_id:   int           = Field(..., description="Collection ID")
+    collection_type: Optional[str] = Field(default="custom", description="'custom' or 'smart'")
+
+
+@mcp.tool(
+    name="shopify_get_collection",
+    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_get_collection(params: GetCollectionInput) -> str:
+    """Retrieve a single collection by ID (custom or smart)."""
+    try:
+        endpoint = f"custom_collections/{params.collection_id}.json" if params.collection_type == "custom" else f"smart_collections/{params.collection_id}.json"
+        key      = "custom_collection" if params.collection_type == "custom" else "smart_collection"
+        data     = await _request("GET", endpoint)
+        return _fmt(data.get(key, data))
+    except Exception as e:
+        return _error(e)
+
+
+class CreateCustomCollectionInput(BaseModel):
+    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
+    title:           str                   = Field(..., min_length=1, description="Collection title")
+    body_html:       Optional[str]         = Field(default=None, description="HTML description")
+    handle:          Optional[str]         = Field(default=None, description="URL handle (slug). Auto-generated from title if omitted")
+    published:       Optional[bool]        = Field(default=False, description="Publish to online store. Default False (hidden)")
+    sort_order:      Optional[str]         = Field(default=None, description="alpha-asc, alpha-desc, best-selling, created, created-desc, manual, price-asc, price-desc")
+    image_src:       Optional[str]         = Field(default=None, description="Public URL of collection image")
+    product_ids:     Optional[List[int]]   = Field(default=None, description="Product IDs to include (manual curation)")
+    metafields:      Optional[List[Dict[str, Any]]] = Field(default=None, description="Inline metafields (e.g. SEO title/description)")
+
+
+@mcp.tool(
+    name="shopify_create_custom_collection",
+    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
+)
+async def shopify_create_custom_collection(params: CreateCustomCollectionInput) -> str:
+    """Create a manually curated (custom) collection where products are added by ID."""
+    try:
+        collection: Dict[str, Any] = {"title": params.title, "published": bool(params.published)}
+        if params.body_html is not None:
+            collection["body_html"] = params.body_html
+        if params.handle:
+            collection["handle"] = params.handle
+        if params.sort_order:
+            collection["sort_order"] = params.sort_order
+        if params.image_src:
+            collection["image"] = {"src": params.image_src}
+        if params.product_ids:
+            collection["collects"] = [{"product_id": pid} for pid in params.product_ids]
+        if params.metafields:
+            collection["metafields"] = params.metafields
+        data = await _request("POST", "custom_collections.json", body={"custom_collection": collection})
+        return _fmt(data.get("custom_collection", data))
+    except Exception as e:
+        return _error(e)
+
+
+class SmartCollectionRule(BaseModel):
+    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
+    column:    str = Field(..., description="tag, title, type, vendor, variant_price, variant_compare_at_price, variant_weight, variant_inventory, variant_title")
+    relation:  str = Field(..., description="equals, not_equals, greater_than, less_than, starts_with, ends_with, contains, not_contains")
+    condition: str = Field(..., description="The value to match, e.g. 'graduation-dress' for a tag rule")
+
+
+class CreateSmartCollectionInput(BaseModel):
+    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
+    title:       str                         = Field(..., min_length=1)
+    rules:       List[SmartCollectionRule]   = Field(..., min_length=1, description="Auto-membership rules")
+    disjunctive: Optional[bool]              = Field(default=False, description="False = AND (all rules), True = OR (any rule)")
+    body_html:   Optional[str]               = Field(default=None)
+    handle:      Optional[str]               = Field(default=None)
+    published:   Optional[bool]              = Field(default=False, description="Publish to online store. Default False (hidden)")
+    sort_order:  Optional[str]               = Field(default=None)
+    image_src:   Optional[str]               = Field(default=None)
+    metafields:  Optional[List[Dict[str, Any]]] = Field(default=None, description="Inline metafields (e.g. SEO title/description)")
+
+
+@mcp.tool(
+    name="shopify_create_smart_collection",
+    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
+)
+async def shopify_create_smart_collection(params: CreateSmartCollectionInput) -> str:
+    """Create a smart collection with auto-membership rules (e.g. tag = 'graduation-dress')."""
+    try:
+        collection: Dict[str, Any] = {
+            "title":       params.title,
+            "rules":       [r.model_dump() for r in params.rules],
+            "disjunctive": bool(params.disjunctive),
+            "published":   bool(params.published),
+        }
+        if params.body_html is not None:
+            collection["body_html"] = params.body_html
+        if params.handle:
+            collection["handle"] = params.handle
+        if params.sort_order:
+            collection["sort_order"] = params.sort_order
+        if params.image_src:
+            collection["image"] = {"src": params.image_src}
+        if params.metafields:
+            collection["metafields"] = params.metafields
+        data = await _request("POST", "smart_collections.json", body={"smart_collection": collection})
+        return _fmt(data.get("smart_collection", data))
+    except Exception as e:
+        return _error(e)
+
+
+class UpdateCollectionInput(BaseModel):
+    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
+    collection_id:   int                          = Field(..., description="Collection ID")
+    collection_type: Optional[str]                = Field(default="custom", description="'custom' or 'smart'")
+    title:           Optional[str]                = Field(default=None)
+    body_html:       Optional[str]                = Field(default=None)
+    handle:          Optional[str]                = Field(default=None)
+    published:       Optional[bool]               = Field(default=None)
+    sort_order:      Optional[str]                = Field(default=None)
+    image_src:       Optional[str]                = Field(default=None)
+    rules:           Optional[List[SmartCollectionRule]] = Field(default=None, description="(Smart only) Replace rules")
+    disjunctive:     Optional[bool]               = Field(default=None, description="(Smart only) AND vs OR")
+
+
+@mcp.tool(
+    name="shopify_update_collection",
+    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_update_collection(params: UpdateCollectionInput) -> str:
+    """Update an existing collection. Only provided fields are changed."""
+    try:
+        is_smart  = params.collection_type == "smart"
+        endpoint  = f"smart_collections/{params.collection_id}.json" if is_smart else f"custom_collections/{params.collection_id}.json"
+        body_key  = "smart_collection" if is_smart else "custom_collection"
+
+        payload: Dict[str, Any] = {"id": params.collection_id}
+        for field in ["title", "body_html", "handle", "sort_order"]:
+            val = getattr(params, field)
+            if val is not None:
+                payload[field] = val
+        if params.published is not None:
+            payload["published"] = params.published
+        if params.image_src:
+            payload["image"] = {"src": params.image_src}
+        if is_smart and params.rules is not None:
+            payload["rules"] = [r.model_dump() for r in params.rules]
+        if is_smart and params.disjunctive is not None:
+            payload["disjunctive"] = params.disjunctive
+
+        data = await _request("PUT", endpoint, body={body_key: payload})
+        return _fmt(data.get(body_key, data))
+    except Exception as e:
+        return _error(e)
+
+
+class DeleteCollectionInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    collection_id:   int           = Field(..., description="Collection ID")
+    collection_type: Optional[str] = Field(default="custom", description="'custom' or 'smart'")
+
+
+@mcp.tool(
+    name="shopify_delete_collection",
+    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_delete_collection(params: DeleteCollectionInput) -> str:
+    """Permanently delete a collection. This cannot be undone."""
+    try:
+        endpoint = f"smart_collections/{params.collection_id}.json" if params.collection_type == "smart" else f"custom_collections/{params.collection_id}.json"
+        await _request("DELETE", endpoint)
+        return _fmt({"deleted": True, "collection_id": params.collection_id})
+    except Exception as e:
+        return _error(e)
+
+
+class AddProductToCollectionInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    collection_id: int           = Field(..., description="Custom collection ID")
+    product_id:    int           = Field(..., description="Product ID to add")
+    position:      Optional[int] = Field(default=None, description="Manual sort position (1-based)")
+
+
+@mcp.tool(
+    name="shopify_add_product_to_collection",
+    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
+)
+async def shopify_add_product_to_collection(params: AddProductToCollectionInput) -> str:
+    """Add a product to a custom (manual) collection. For smart collections, tag the product instead."""
+    try:
+        collect: Dict[str, Any] = {"collection_id": params.collection_id, "product_id": params.product_id}
+        if params.position:
+            collect["position"] = params.position
+        data = await _request("POST", "collects.json", body={"collect": collect})
+        return _fmt(data.get("collect", data))
+    except Exception as e:
+        return _error(e)
+
+
+class RemoveProductFromCollectionInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    collect_id: int = Field(..., description="The collect ID linking product<>collection (from list_collects or add response)")
+
+
+@mcp.tool(
+    name="shopify_remove_product_from_collection",
+    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_remove_product_from_collection(params: RemoveProductFromCollectionInput) -> str:
+    """Remove a product from a custom collection by deleting its collect record."""
+    try:
+        await _request("DELETE", f"collects/{params.collect_id}.json")
+        return _fmt({"deleted": True, "collect_id": params.collect_id})
+    except Exception as e:
+        return _error(e)
+
+
+class ListCollectsInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    collection_id: Optional[int] = Field(default=None, description="Filter by collection")
+    product_id:    Optional[int] = Field(default=None, description="Filter by product")
+    limit:         Optional[int] = Field(default=50, ge=1, le=250)
+
+
+@mcp.tool(
+    name="shopify_list_collects",
+    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_list_collects(params: ListCollectsInput) -> str:
+    """List collect records (product↔collection links). Use to find a collect_id for removal."""
+    try:
+        p: Dict[str, Any] = {"limit": params.limit}
+        if params.collection_id:
+            p["collection_id"] = params.collection_id
+        if params.product_id:
+            p["product_id"] = params.product_id
+        data = await _request("GET", "collects.json", params=p)
+        collects = data.get("collects", [])
+        return _fmt({"count": len(collects), "collects": collects})
+    except Exception as e:
+        return _error(e)
+
+
 # ═══════════════════════════════════════════════════════════════════════════
 # INVENTORY
 # ═══════════════════════════════════════════════════════════════════════════
@@ -929,6 +1169,582 @@
     except Exception as e:
         return _error(e)
 
+
+# ═══════════════════════════════════════════════════════════════════════════
+# PAGES (About, Shipping, Returns, etc. — requires read_content/write_content scopes)
+# ═══════════════════════════════════════════════════════════════════════════
+
+class ListPagesInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    limit:       Optional[int] = Field(default=50, ge=1, le=250)
+    since_id:    Optional[int] = Field(default=None)
+    title:       Optional[str] = Field(default=None, description="Filter by exact title")
+    handle:      Optional[str] = Field(default=None, description="Filter by URL handle")
+    fields:      Optional[str] = Field(default=None, description="Comma-separated fields to include")
+
+
+@mcp.tool(
+    name="shopify_list_pages",
+    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_list_pages(params: ListPagesInput) -> str:
+    """List pages on the store (About, Shipping, Returns, etc.)."""
+    try:
+        p: Dict[str, Any] = {"limit": params.limit}
+        for field in ["since_id", "title", "handle", "fields"]:
+            val = getattr(params, field)
+            if val is not None:
+                p[field] = val
+        data  = await _request("GET", "pages.json", params=p)
+        pages = data.get("pages", [])
+        return _fmt({"count": len(pages), "pages": pages})
+    except Exception as e:
+        return _error(e)
+
+
+class GetPageInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    page_id: int = Field(..., description="Page ID")
+
+
+@mcp.tool(
+    name="shopify_get_page",
+    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_get_page(params: GetPageInput) -> str:
+    """Retrieve a single page by ID, including its body_html."""
+    try:
+        data = await _request("GET", f"pages/{params.page_id}.json")
+        return _fmt(data.get("page", data))
+    except Exception as e:
+        return _error(e)
+
+
+class CreatePageInput(BaseModel):
+    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
+    title:      str                          = Field(..., min_length=1)
+    body_html:  Optional[str]                = Field(default=None, description="HTML content")
+    author:     Optional[str]                = Field(default=None)
+    handle:     Optional[str]                = Field(default=None, description="URL handle. Auto-generated from title if omitted")
+    published:  Optional[bool]               = Field(default=False, description="Publish immediately. Default False (draft)")
+    metafields: Optional[List[Dict[str, Any]]] = Field(default=None, description="Inline metafields (e.g. SEO title/description)")
+
+
+@mcp.tool(
+    name="shopify_create_page",
+    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
+)
+async def shopify_create_page(params: CreatePageInput) -> str:
+    """Create a new page (About, Shipping, Returns, etc.)."""
+    try:
+        page: Dict[str, Any] = {"title": params.title, "published": bool(params.published)}
+        for field in ["body_html", "author", "handle"]:
+            val = getattr(params, field)
+            if val is not None:
+                page[field] = val
+        if params.metafields:
+            page["metafields"] = params.metafields
+        data = await _request("POST", "pages.json", body={"page": page})
+        return _fmt(data.get("page", data))
+    except Exception as e:
+        return _error(e)
+
+
+class UpdatePageInput(BaseModel):
+    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
+    page_id:   int           = Field(..., description="Page ID")
+    title:     Optional[str] = Field(default=None)
+    body_html: Optional[str] = Field(default=None)
+    author:    Optional[str] = Field(default=None)
+    handle:    Optional[str] = Field(default=None)
+    published: Optional[bool] = Field(default=None)
+
+
+@mcp.tool(
+    name="shopify_update_page",
+    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_update_page(params: UpdatePageInput) -> str:
+    """Update an existing page. Only provided fields are changed."""
+    try:
+        payload: Dict[str, Any] = {"id": params.page_id}
+        for field in ["title", "body_html", "author", "handle"]:
+            val = getattr(params, field)
+            if val is not None:
+                payload[field] = val
+        if params.published is not None:
+            payload["published"] = params.published
+        data = await _request("PUT", f"pages/{params.page_id}.json", body={"page": payload})
+        return _fmt(data.get("page", data))
+    except Exception as e:
+        return _error(e)
+
+
+class DeletePageInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    page_id: int = Field(..., description="Page ID")
+
+
+@mcp.tool(
+    name="shopify_delete_page",
+    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_delete_page(params: DeletePageInput) -> str:
+    """Permanently delete a page. This cannot be undone."""
+    try:
+        await _request("DELETE", f"pages/{params.page_id}.json")
+        return _fmt({"deleted": True, "page_id": params.page_id})
+    except Exception as e:
+        return _error(e)
+
+
+# ═══════════════════════════════════════════════════════════════════════════
+# METAFIELDS (SEO title/description, size charts, custom data on any resource)
+# ═══════════════════════════════════════════════════════════════════════════
+#
+# Shopify stores SEO title and meta description as metafields:
+#   namespace = "global", key = "title_tag"        (single_line_text_field)
+#   namespace = "global", key = "description_tag"  (multi_line_text_field)
+#
+# Use shopify_set_seo for a simple SEO title/description workflow, or
+# shopify_set_metafield for any other metafield.
+
+_METAFIELD_OWNER_PATHS = {
+    "product":    "products",
+    "collection": "collections",
+    "page":       "pages",
+    "blog":       "blogs",
+    "article":    "articles",
+    "variant":    "variants",
+    "customer":   "customers",
+    "order":      "orders",
+    "shop":       None,  # Shop-level metafields use /metafields.json directly
+}
+
+
+def _metafield_endpoint(owner_resource: str, owner_id: Optional[int], metafield_id: Optional[int] = None) -> str:
+    if owner_resource not in _METAFIELD_OWNER_PATHS:
+        raise ValueError(f"Unknown owner_resource '{owner_resource}'. Must be one of: {', '.join(_METAFIELD_OWNER_PATHS)}")
+    base = _METAFIELD_OWNER_PATHS[owner_resource]
+    if owner_resource == "shop":
+        return f"metafields/{metafield_id}.json" if metafield_id else "metafields.json"
+    if owner_id is None:
+        raise ValueError(f"owner_id is required for owner_resource='{owner_resource}'")
+    if metafield_id:
+        return f"{base}/{owner_id}/metafields/{metafield_id}.json"
+    return f"{base}/{owner_id}/metafields.json"
+
+
+class ListMetafieldsInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    owner_resource: str           = Field(..., description="product, collection, page, blog, article, variant, customer, order, or shop")
+    owner_id:       Optional[int] = Field(default=None, description="Required except when owner_resource='shop'")
+    namespace:      Optional[str] = Field(default=None, description="Filter by namespace, e.g. 'global' for SEO fields")
+    key:            Optional[str] = Field(default=None, description="Filter by key, e.g. 'title_tag'")
+    limit:          Optional[int] = Field(default=50, ge=1, le=250)
+
+
+@mcp.tool(
+    name="shopify_list_metafields",
+    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_list_metafields(params: ListMetafieldsInput) -> str:
+    """List metafields on a resource. Useful to check existing SEO title/description before updating."""
+    try:
+        endpoint = _metafield_endpoint(params.owner_resource, params.owner_id)
+        p: Dict[str, Any] = {"limit": params.limit}
+        if params.namespace:
+            p["namespace"] = params.namespace
+        if params.key:
+            p["key"] = params.key
+        data       = await _request("GET", endpoint, params=p)
+        metafields = data.get("metafields", [])
+        return _fmt({"count": len(metafields), "metafields": metafields})
+    except Exception as e:
+        return _error(e)
+
+
+class SetMetafieldInput(BaseModel):
+    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
+    owner_resource: str           = Field(..., description="product, collection, page, blog, article, variant, customer, order, or shop")
+    owner_id:       Optional[int] = Field(default=None, description="Required except when owner_resource='shop'")
+    namespace:      str           = Field(..., description="Metafield namespace, e.g. 'global' for SEO, 'custom' for custom fields")
+    key:            str           = Field(..., description="Metafield key, e.g. 'title_tag', 'description_tag', 'size_chart'")
+    value:          str           = Field(..., description="The value to set (strings only — for numbers/JSON, pass as a string)")
+    type:           Optional[str] = Field(default="single_line_text_field", description="single_line_text_field, multi_line_text_field, number_integer, boolean, json, url, etc.")
+
+
+@mcp.tool(
+    name="shopify_set_metafield",
+    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_set_metafield(params: SetMetafieldInput) -> str:
+    """Create or update a metafield on a product, collection, page, etc. Upserts by (namespace, key)."""
+    try:
+        endpoint = _metafield_endpoint(params.owner_resource, params.owner_id)
+        metafield = {
+            "namespace": params.namespace,
+            "key":       params.key,
+            "value":     params.value,
+            "type":      params.type,
+        }
+        # Shopify upserts on POST when (namespace, key) already exists on the owner
+        data = await _request("POST", endpoint, body={"metafield": metafield})
+        return _fmt(data.get("metafield", data))
+    except Exception as e:
+        return _error(e)
+
+
+class DeleteMetafieldInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    owner_resource: str           = Field(..., description="product, collection, page, blog, article, variant, customer, order, or shop")
+    owner_id:       Optional[int] = Field(default=None, description="Required except when owner_resource='shop'")
+    metafield_id:   int           = Field(..., description="The metafield ID (from list_metafields)")
+
+
+@mcp.tool(
+    name="shopify_delete_metafield",
+    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_delete_metafield(params: DeleteMetafieldInput) -> str:
+    """Permanently delete a metafield by ID."""
+    try:
+        endpoint = _metafield_endpoint(params.owner_resource, params.owner_id, params.metafield_id)
+        await _request("DELETE", endpoint)
+        return _fmt({"deleted": True, "metafield_id": params.metafield_id})
+    except Exception as e:
+        return _error(e)
+
+
+class SetSeoInput(BaseModel):
+    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
+    owner_resource:   str           = Field(..., description="product, collection, page, or article")
+    owner_id:         int           = Field(..., description="Product/collection/page/article ID")
+    seo_title:        Optional[str] = Field(default=None, description="SEO title tag (~50-60 characters recommended)")
+    seo_description:  Optional[str] = Field(default=None, description="Meta description (~120-155 characters recommended)")
+
+
+@mcp.tool(
+    name="shopify_set_seo",
+    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_set_seo(params: SetSeoInput) -> str:
+    """Set SEO title and/or meta description on a product, collection, page, or article. Convenience wrapper around set_metafield."""
+    if params.owner_resource not in ("product", "collection", "page", "article"):
+        return _error(ValueError(f"owner_resource must be 'product', 'collection', 'page', or 'article' (got '{params.owner_resource}')"))
+    if params.seo_title is None and params.seo_description is None:
+        return _error(ValueError("Provide at least one of seo_title or seo_description"))
+
+    results: Dict[str, Any] = {}
+    try:
+        endpoint = _metafield_endpoint(params.owner_resource, params.owner_id)
+        if params.seo_title is not None:
+            body = {"metafield": {
+                "namespace": "global",
+                "key":       "title_tag",
+                "value":     params.seo_title,
+                "type":      "single_line_text_field",
+            }}
+            data = await _request("POST", endpoint, body=body)
+            results["title_tag"] = data.get("metafield", data)
+        if params.seo_description is not None:
+            body = {"metafield": {
+                "namespace": "global",
+                "key":       "description_tag",
+                "value":     params.seo_description,
+                "type":      "multi_line_text_field",
+            }}
+            data = await _request("POST", endpoint, body=body)
+            results["description_tag"] = data.get("metafield", data)
+        return _fmt(results)
+    except Exception as e:
+        return _error(e)
+
+
+# ═══════════════════════════════════════════════════════════════════════════
+# BLOGS (containers — a store can have multiple blogs, e.g. "News", "Style Guide")
+# ═══════════════════════════════════════════════════════════════════════════
+
+class ListBlogsInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    limit:    Optional[int] = Field(default=50, ge=1, le=250)
+    since_id: Optional[int] = Field(default=None)
+    handle:   Optional[str] = Field(default=None, description="Filter by handle")
+    fields:   Optional[str] = Field(default=None)
+
+
+@mcp.tool(
+    name="shopify_list_blogs",
+    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_list_blogs(params: ListBlogsInput) -> str:
+    """List blogs on the store. A blog is a container that holds articles."""
+    try:
+        p: Dict[str, Any] = {"limit": params.limit}
+        for field in ["since_id", "handle", "fields"]:
+            val = getattr(params, field)
+            if val is not None:
+                p[field] = val
+        data  = await _request("GET", "blogs.json", params=p)
+        blogs = data.get("blogs", [])
+        return _fmt({"count": len(blogs), "blogs": blogs})
+    except Exception as e:
+        return _error(e)
+
+
+class GetBlogInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    blog_id: int = Field(..., description="Blog ID")
+
+
+@mcp.tool(
+    name="shopify_get_blog",
+    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_get_blog(params: GetBlogInput) -> str:
+    """Retrieve a single blog by ID."""
+    try:
+        data = await _request("GET", f"blogs/{params.blog_id}.json")
+        return _fmt(data.get("blog", data))
+    except Exception as e:
+        return _error(e)
+
+
+class CreateBlogInput(BaseModel):
+    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
+    title:          str                          = Field(..., min_length=1)
+    handle:         Optional[str]                = Field(default=None, description="URL handle. Auto-generated from title")
+    commentable:    Optional[str]                = Field(default="no", description="no, moderate, or yes")
+    feedburner:     Optional[str]                = Field(default=None, description="FeedBurner URL")
+    feedburner_url: Optional[str]                = Field(default=None)
+    tags:           Optional[str]                = Field(default=None, description="Comma-separated tags (used across articles)")
+    template_suffix: Optional[str]               = Field(default=None, description="Alternate theme template suffix")
+    metafields:     Optional[List[Dict[str, Any]]] = Field(default=None)
+
+
+@mcp.tool(
+    name="shopify_create_blog",
+    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
+)
+async def shopify_create_blog(params: CreateBlogInput) -> str:
+    """Create a new blog (a container for articles)."""
+    try:
+        blog: Dict[str, Any] = {"title": params.title}
+        for field in ["handle", "commentable", "feedburner", "feedburner_url", "tags", "template_suffix"]:
+            val = getattr(params, field)
+            if val is not None:
+                blog[field] = val
+        if params.metafields:
+            blog["metafields"] = params.metafields
+        data = await _request("POST", "blogs.json", body={"blog": blog})
+        return _fmt(data.get("blog", data))
+    except Exception as e:
+        return _error(e)
+
+
+class UpdateBlogInput(BaseModel):
+    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
+    blog_id:         int           = Field(..., description="Blog ID")
+    title:           Optional[str] = Field(default=None)
+    handle:          Optional[str] = Field(default=None)
+    commentable:     Optional[str] = Field(default=None)
+    tags:            Optional[str] = Field(default=None)
+    template_suffix: Optional[str] = Field(default=None)
+
+
+@mcp.tool(
+    name="shopify_update_blog",
+    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_update_blog(params: UpdateBlogInput) -> str:
+    """Update an existing blog's settings."""
+    try:
+        payload: Dict[str, Any] = {"id": params.blog_id}
+        for field in ["title", "handle", "commentable", "tags", "template_suffix"]:
+            val = getattr(params, field)
+            if val is not None:
+                payload[field] = val
+        data = await _request("PUT", f"blogs/{params.blog_id}.json", body={"blog": payload})
+        return _fmt(data.get("blog", data))
+    except Exception as e:
+        return _error(e)
+
+
+class DeleteBlogInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    blog_id: int = Field(..., description="Blog ID")
+
+
+@mcp.tool(
+    name="shopify_delete_blog",
+    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_delete_blog(params: DeleteBlogInput) -> str:
+    """Permanently delete a blog and ALL its articles. This cannot be undone."""
+    try:
+        await _request("DELETE", f"blogs/{params.blog_id}.json")
+        return _fmt({"deleted": True, "blog_id": params.blog_id})
+    except Exception as e:
+        return _error(e)
+
+
+# ═══════════════════════════════════════════════════════════════════════════
+# ARTICLES (blog posts)
+# ═══════════════════════════════════════════════════════════════════════════
+
+class ListArticlesInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    blog_id:          Optional[int] = Field(default=None, description="Scope to one blog. Omit to list all articles")
+    limit:            Optional[int] = Field(default=50, ge=1, le=250)
+    since_id:         Optional[int] = Field(default=None)
+    handle:           Optional[str] = Field(default=None)
+    tag:              Optional[str] = Field(default=None, description="Filter by tag")
+    author:           Optional[str] = Field(default=None)
+    published_status: Optional[str] = Field(default=None, description="published, unpublished, or any")
+    fields:           Optional[str] = Field(default=None)
+
+
+@mcp.tool(
+    name="shopify_list_articles",
+    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_list_articles(params: ListArticlesInput) -> str:
+    """List articles, optionally scoped to a specific blog."""
+    try:
+        p: Dict[str, Any] = {"limit": params.limit}
+        for field in ["since_id", "handle", "tag", "author", "published_status", "fields"]:
+            val = getattr(params, field)
+            if val is not None:
+                p[field] = val
+        endpoint = f"blogs/{params.blog_id}/articles.json" if params.blog_id else "articles.json"
+        data     = await _request("GET", endpoint, params=p)
+        articles = data.get("articles", [])
+        return _fmt({"count": len(articles), "articles": articles})
+    except Exception as e:
+        return _error(e)
+
+
+class GetArticleInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    blog_id:    int = Field(..., description="Parent blog ID")
+    article_id: int = Field(..., description="Article ID")
+
+
+@mcp.tool(
+    name="shopify_get_article",
+    annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_get_article(params: GetArticleInput) -> str:
+    """Retrieve a single article by ID, including its body_html."""
+    try:
+        data = await _request("GET", f"blogs/{params.blog_id}/articles/{params.article_id}.json")
+        return _fmt(data.get("article", data))
+    except Exception as e:
+        return _error(e)
+
+
+class CreateArticleInput(BaseModel):
+    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
+    blog_id:         int                          = Field(..., description="Parent blog ID (use list_blogs to find it)")
+    title:           str                          = Field(..., min_length=1)
+    body_html:       Optional[str]                = Field(default=None, description="HTML content of the post")
+    author:          Optional[str]                = Field(default=None, description="Author name")
+    summary_html:    Optional[str]                = Field(default=None, description="HTML excerpt shown in blog listing")
+    tags:            Optional[str]                = Field(default=None, description="Comma-separated tags")
+    handle:          Optional[str]                = Field(default=None)
+    published:       Optional[bool]               = Field(default=False, description="Publish immediately. Default False (draft)")
+    published_at:    Optional[str]                = Field(default=None, description="ISO 8601 datetime to schedule future publishing")
+    image_src:       Optional[str]                = Field(default=None, description="Featured image URL")
+    image_alt:       Optional[str]                = Field(default=None, description="Featured image alt text (SEO)")
+    template_suffix: Optional[str]                = Field(default=None)
+    metafields:      Optional[List[Dict[str, Any]]] = Field(default=None, description="Inline metafields (e.g. SEO title/description)")
+
+
+@mcp.tool(
+    name="shopify_create_article",
+    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True},
+)
+async def shopify_create_article(params: CreateArticleInput) -> str:
+    """Create a new blog article. Use list_blogs first to find the blog_id."""
+    try:
+        article: Dict[str, Any] = {"title": params.title, "published": bool(params.published)}
+        for field in ["body_html", "author", "summary_html", "tags", "handle", "published_at", "template_suffix"]:
+            val = getattr(params, field)
+            if val is not None:
+                article[field] = val
+        if params.image_src:
+            img: Dict[str, Any] = {"src": params.image_src}
+            if params.image_alt:
+                img["alt"] = params.image_alt
+            article["image"] = img
+        if params.metafields:
+            article["metafields"] = params.metafields
+        data = await _request("POST", f"blogs/{params.blog_id}/articles.json", body={"article": article})
+        return _fmt(data.get("article", data))
+    except Exception as e:
+        return _error(e)
+
+
+class UpdateArticleInput(BaseModel):
+    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
+    blog_id:         int           = Field(..., description="Parent blog ID")
+    article_id:      int           = Field(..., description="Article ID")
+    title:           Optional[str] = Field(default=None)
+    body_html:       Optional[str] = Field(default=None)
+    author:          Optional[str] = Field(default=None)
+    summary_html:    Optional[str] = Field(default=None)
+    tags:            Optional[str] = Field(default=None)
+    handle:          Optional[str] = Field(default=None)
+    published:       Optional[bool] = Field(default=None)
+    published_at:    Optional[str] = Field(default=None)
+    image_src:       Optional[str] = Field(default=None)
+    image_alt:       Optional[str] = Field(default=None)
+    template_suffix: Optional[str] = Field(default=None)
+
+
+@mcp.tool(
+    name="shopify_update_article",
+    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_update_article(params: UpdateArticleInput) -> str:
+    """Update an existing article. Only provided fields are changed."""
+    try:
+        payload: Dict[str, Any] = {"id": params.article_id}
+        for field in ["title", "body_html", "author", "summary_html", "tags", "handle", "published_at", "template_suffix"]:
+            val = getattr(params, field)
+            if val is not None:
+                payload[field] = val
+        if params.published is not None:
+            payload["published"] = params.published
+        if params.image_src:
+            img: Dict[str, Any] = {"src": params.image_src}
+            if params.image_alt:
+                img["alt"] = params.image_alt
+            payload["image"] = img
+        data = await _request("PUT", f"blogs/{params.blog_id}/articles/{params.article_id}.json", body={"article": payload})
+        return _fmt(data.get("article", data))
+    except Exception as e:
+        return _error(e)
+
+
+class DeleteArticleInput(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+    blog_id:    int = Field(..., description="Parent blog ID")
+    article_id: int = Field(..., description="Article ID")
+
+
+@mcp.tool(
+    name="shopify_delete_article",
+    annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": True, "openWorldHint": True},
+)
+async def shopify_delete_article(params: DeleteArticleInput) -> str:
+    """Permanently delete an article. This cannot be undone."""
+    try:
+        await _request("DELETE", f"blogs/{params.blog_id}/articles/{params.article_id}.json")
+        return _fmt({"deleted": True, "article_id": params.article_id})
+    except Exception as e:
+        return _error(e)
+
 
 # ---------------------------------------------------------------------------
 # Entrypoint
