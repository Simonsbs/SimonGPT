// src/app/api/logout/route.ts

import { NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function GET() {
  const cookieStore = await cookies();
  cookieStore.delete("auth_token");

  return NextResponse.redirect("/login");
}
